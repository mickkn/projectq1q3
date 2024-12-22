"""
:File:        q1q3utility.py

:Details:     Utility Module to Decompile Q3 Maps to Q1 Maps.

:Date:        20-12-2024
:Author:      Mick K
"""

import argparse
import csv
import glob
import io
import logging
import math
import os
import platform
import re
import shutil
import struct
import subprocess
import time
from collections import defaultdict
from multiprocessing import Pool
from typing import Dict, List, Tuple

from PIL import Image
from vgio import quake
from vgio.quake import lmp, wad


class Q1Q3Util(object):
    """Class to decompile Q3 maps to Q1 maps.

    Args:
        arguments (argparse.Namespace): Arguments from the command line.
    """
    def __init__(self, arguments: argparse.Namespace):
        self._bsp_path = arguments.bsp
        self._csv_path = arguments.csv
        self._map_path = arguments.map
        self._tex_path = arguments.tex
        self._bmp_size = arguments.size
        self._cpus = arguments.cpus
        self._map_output = None
        self._map_output_textured = None
        self._tex_output = None
        self._wad_output = None
        self._wad_type = arguments.type
        self._tex_placements = {}
        self._q3map2_path = None
        self._found_textures = defaultdict(int)
        self._textures_not_found = []
        self._potentially_missing_textures = []
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

    def run(self):
        """Function to run the utility."""
        if self._map_path is None:
            if self._bsp_path is None:
                print("No map or bsp file path provided.")
                print("Read the help for more information.")
                print(f"python {os.path.basename(__file__)} -h")
                exit(1)
            self._map_path = self._bsp_path.replace(".bsp", "_converted.map")
            self._decompile()
        else:
            self._map_output = self._map_path.replace(".map", "_textured.map")
            self._logger.info(f"Skipping decompile step, using existing map: {self._map_path}")
        self._replace_textures()
        path = self._create_24bit_folder(self._map_output.replace(".map", "_24bit"))
        path = self._create_bmp(path)
        self._create_wad(path)
        self._get_potentially_missing_textures()

    def _decompile(self):
        """Function to decompile the Q3/QL map to a Q1 map."""

        self._logger.info(f"Decompiling map: {self._bsp_path}")

        if self._bsp_path is None:
            raise ValueError("No bsp file path provided.")

        if platform.system() == "Windows":
            self._q3map2_path = os.path.join(os.path.dirname(__file__), "q3map2.exe")
        elif platform.system() == "Linux":
            self._q3map2_path = os.path.join(os.path.dirname(__file__), "q3map2.x86")
        else:
            raise ValueError("Unsupported OS platform.")

        # Define the path to the decompiled map.
        self._map_output = self._bsp_path.replace(".bsp", "_converted.map")

        try:
            subprocess.run(
                " ".join(
                    [
                        self._q3map2_path,
                        "-convert",
                        "-format",
                        "map",
                        f'"{self._bsp_path}"',
                    ]
                ),
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except subprocess.CalledProcessError:
            self._logger.warning("Error decompiling the map, probably because it is version 47. Trying again...")

            try:
                # Use QuakeLive approach to decompile the map
                subprocess.run(
                    " ".join(
                        [
                            self._q3map2_path,
                            "-convert",
                            "-game",
                            "et",
                            "-format",
                            "map",
                            f'"{self._bsp_path}"',
                        ]
                    ),
                    shell=True,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    " ".join(
                        [
                            self._q3map2_path,
                            "-convert",
                            "-game",
                            "et",
                            "-format",
                            "quake3",
                            f'"{self._bsp_path.replace(".map", "_converted.map")}"',
                        ]
                    ),
                    shell=True,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            except subprocess.CalledProcessError as e:
                self._logger.error(f"Error decompiling the map: {e}")

        self._logger.info("Map decompiled successfully.")
        self._logger.info("Map path: %s" % self._map_output)

    def _replace_textures(self):
        """Function to replace the textures in the decompiled map with multiprocessing."""
        start = time.time()
        self._load_csv()

        # Precompile the regex for replacements
        replacements = self._tex_placements
        regex = re.compile(r"(\b" + r"\b|\b".join(map(re.escape, replacements.keys())) + r"\b)")

        # Read the file in chunks of lines
        with open(self._map_path, "r") as f:
            lines = f.readlines()
        chunk_size = len(lines) // self._cpus  # Divide into processes
        chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]

        # Process chunks in parallel
        with Pool(processes=self._cpus) as pool:
            results = pool.starmap(
                Q1Q3Util._replace_textures_worker,
                [(chunk, regex, replacements) for chunk in chunks],
            )

        # Collect results and write output
        self._map_output_textured = self._map_output.replace(".map", "_textured.map")
        with open(self._map_output_textured, "w") as f_out:
            for replaced_lines, found in results:
                f_out.writelines(replaced_lines)
                for key, count in found.items():
                    self._found_textures[key] += count  # Aggregate into the class variable

        # Log replacements summary
        for original, replacement in replacements.items():
            if original in self._found_textures:
                self._logger.info(f"Replaced '{original}' with '{replacement}' {self._found_textures[original]} times.")

        self._logger.info(f"Textures replaced successfully, in {time.time() - start:.2f} seconds.")

    @staticmethod
    def _replace_textures_worker(chunk, regex, replacements) -> Tuple[List[str], Dict[str, int]]:
        """Static method to replace textures for a chunk of lines.

        Args
            chunk: List of lines to process.
            regex: Compiled regex for replacements.
            replacements: Dictionary of texture replacements.

        Returns:
            Tuple: List of replaced lines and dictionary of found replacements.
        """
        result = []
        found_replacements = defaultdict(int)  # To store counts of replacements in this chunk
        for line in chunk:

            def replacer(match):
                original = match.group(0)
                found_replacements[original] += 1
                return replacements[original]

            line = regex.sub(replacer, line)  # Replace textures
            line = line.replace(" 0.5 0.5 ", " 0 0 ")  # Fix texture alignment
            result.append(line)

        return result, found_replacements

    @staticmethod
    def _resize_textures(image_path: str, max_size: int = 256) -> None:
        """Resize an image to the nearest power of two dimensions,
           ensuring it does not exceed max_size.

        Args:
            image_path: Path to the image to resize.
            max_size: Maximum size for the image (default: 256).

        Raises:
            ValueError: If the image path does not exist
        """
        image = Image.open(image_path)
        width, height = image.size

        # Calculate nearest powers of two for width and height
        new_width = max(8, 2 ** round(math.log2(width)))
        new_height = max(8, 2 ** round(math.log2(height)))

        # Adjust dimensions if they exceed max_size
        if new_width > max_size or new_height > max_size:
            scaling_factor = min(max_size / new_width, max_size / new_height)
            new_width = int(new_width * scaling_factor)
            new_height = int(new_height * scaling_factor)

        # Resize and save only if the dimensions have changed
        if (new_width, new_height) != (width, height):
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            image.save(image_path)

    def find_and_copy(self, src: str, dst: str) -> None:
        """Function to find and copy a texture to a destination folder.

        Args:
            src: Source texture to find.
            dst: Destination folder to copy the texture to.
        """
        path = src.split("/")
        path[-1] = path[-1] + ".*"
        search_pattern = os.path.join(self._tex_path, *path)
        found = glob.glob(search_pattern)

        if found:
            found = found[0]
            dst_file = f"{self._tex_placements[src]}.{found.split('.')[-1]}"
            dst_path = os.path.join(dst, dst_file)
            self._logger.info(f"{found} -> {dst_path}")
            os.makedirs(dst, exist_ok=True)
            shutil.copy(found, dst_path)
            self._resize_textures(dst_path)

    def _create_24bit_folder(self, output_folder: str) -> str:
        """Function to create a 24bit folder with the textures in the map.

        Args:
            output_folder: Output folder to create.

        Raises:
            ValueError: If no textures path is provided.

        Return:
            str: Path to the 24bit folder.
        """
        if self._tex_path is None:
            raise ValueError("No textures path provided.")

        os.makedirs(output_folder, exist_ok=True)

        # Copy the found textures to the 24bit folder.
        self._logger.info(f"Creating 24bit folder: {output_folder}")
        for tex in self._found_textures.keys():
            self.find_and_copy(tex, os.path.join(output_folder))

        return output_folder

    def _create_bmp(self, output_folder: str) -> str:
        """Function to create a WAD file from the 24bit textures found for the map.

        Args:
            output_folder: Output folder to create the BMP files.

        Returns:
            str: Path to the BMP folder.
        """
        self._logger.info("Creating BMP file(s)...")
        bmp_folder = os.path.join(output_folder, "bmp")
        os.makedirs(bmp_folder, exist_ok=True)

        # Convert all images in output_folder to 8-bit BMPs
        for img in os.listdir(output_folder):

            # Only continue on image files
            if os.path.isfile(os.path.join(output_folder, img)):

                # Copy the image to the bmp folder, and change the extension to .bmp
                img_path = os.path.join(output_folder, img)
                bmp_path = os.path.join(bmp_folder, os.path.splitext(img)[0] + ".bmp")
                shutil.copy(img_path, bmp_path)

        palette = Image.open("qpalette.png")

        # Convert the BMP's to actually be 8-bit
        for img in os.listdir(bmp_folder):
            img_path = os.path.join(bmp_folder, img)
            self._resize_textures(img_path, self._bmp_size)
            img = Image.open(img_path)
            img = img.convert("P", palette=palette)
            img.save(img_path)

        return bmp_folder

    def _create_wad(self, output_folder: str) -> None:
        """Create a WAD file from the BMP textures converted from 24-bit textures."""
        self._logger.info(f"Creating WAD file using {self._wad_type} data type...")
        self._wad_output = self._map_output.replace(".map", ".wad")

        # Flatten palette
        palette = [color for p in quake.palette for color in p]
        palette_image = Image.frombytes("P", (16, 16), bytes(palette))
        palette_image.putpalette(palette)

        with wad.WadFile(self._wad_output, "w") as wad_file:
            self._logger.info(f"Archive: {os.path.basename(self._wad_output)}")

            for file in os.listdir(output_folder):
                img_path = os.path.join(output_folder, file)
                self._logger.info(f"Processing: {file}")

                try:
                    if self._wad_type == "LUMP":
                        wad_file.write(img_path)

                    else:
                        img = Image.open(img_path).convert(mode="RGB")
                        img = img.quantize(palette=palette_image)
                        name = os.path.basename(file).split(".")[0]

                        if self._wad_type == "QPIC":
                            self._add_qpic_to_wad(img, name, wad_file)
                        else:
                            self._add_miptex_to_wad(img, name, wad_file)

                except Exception as e:
                    self._logger.error(f"Error adding {file}: {e}")

    def _add_qpic_to_wad(self, img: Image.Image, name: str, wad_file: wad.WadFile) -> None:
        """Helper to add a QPIC image to the WAD."""
        pixels = img.tobytes()
        qpic = lmp.Lmp()
        qpic.width, qpic.height = img.width, img.height
        qpic.pixels = pixels

        buff = io.BytesIO()
        lmp.Lmp.write(buff, qpic)
        file_size = buff.tell()
        buff.seek(0)

        info = wad.WadInfo(name)
        info.file_size = file_size
        info.disk_size = file_size
        info.compression = wad.CompressionType.NONE
        info.type = wad.LumpType.QPIC

        self._logger.info(f"  Adding QPIC: {name}")
        wad_file.writestr(info, buff)

    def _add_miptex_to_wad(self, img: Image.Image, name: str, wad_file: wad.WadFile) -> None:
        """Helper to add a MIPTEX image to the WAD."""
        mip = wad.Miptexture()
        mip.name = name
        mip.width, mip.height = img.width, img.height
        mip.offsets = [40]
        mip.pixels = []

        for i in range(4):  # Generate mipmaps
            resized_image = img.resize((img.width // (2**i), img.height // (2**i)))
            data = resized_image.tobytes()
            mip.pixels += struct.unpack(f"<{len(data)}B", data)
            if i < 3:
                mip.offsets.append(mip.offsets[-1] + len(data))

        buff = io.BytesIO()
        wad.Miptexture.write(buff, mip)
        buff.seek(0)

        info = wad.WadInfo(name)
        info.file_size = 40 + len(mip.pixels)
        info.disk_size = info.file_size
        info.compression = wad.CompressionType.NONE
        info.type = wad.LumpType.MIPTEX

        self._logger.info(f"  Adding MIPTEX: {name}")
        wad_file.writestr(info, buff)

    def _get_potentially_missing_textures(self) -> None:
        """Function to get potentially missing textures."""
        self._logger.info(f"Checking for potentially missing textures in {self._map_output_textured}...")

        # Get all textures from the map
        with open(self._map_output_textured, "r") as f:
            lines = f.readlines()

        # Regex to match strings with one or more slashes, excluding extensions and quotes
        pattern = re.compile(r'(?<=\s)[^/\s"]+(?:/[^/\s"]+)+(?!\.[a-zA-Z0-9]{2,4})(?=\s)')

        # Use a set to store unique matches
        unique_matches = set()

        for line in lines:
            matches = re.findall(pattern, line)
            unique_matches.update(matches)  # Add all matches from the current line to the set

        if len(unique_matches) > 0:
            self._logger.info(f"Potentially missing textures found: {len(unique_matches)}")
            self._logger.info("Writing textures to potentially_missing.txt...")

            # Sort the matches and write them to a file
            unique_matches = sorted(list(unique_matches))

            with open("potentially_missing.txt", "w") as f:
                for match in unique_matches:
                    f.write(f"{match}\n")

            # Write a new custom csv for the potentially missing textures
            csv_out = self._map_output.replace(".map", "_miss_textures.csv")
            self._logger.info(f"Writing potentially missing textures to {csv_out}...")
            with open(csv_out, "w") as f:

                # Write the header
                f.write("Q3TEX;NAME IDEA, CHECK BEFORE INPUTTING IN MAIN CSV\n")

                for match in unique_matches:
                    # Make a texture name clamped to 15 chars in CAPS based on the original texture
                    match_conv = match.split("/")[-1].upper()[:15]
                    f.write(f"{match};{match_conv}\n")

    def _load_csv(self) -> None:
        """Function to load the csv file with texture replacements.

        Raises:
            ValueError: If no csv file path is provided.
        """

        if self._csv_path is None:
            raise ValueError("No csv file path provided.")

        with open(self._csv_path, "r") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                q3tex, q1tex = row[:2]
                self._tex_placements[q3tex] = q1tex

        self._logger.info(f"CSV file loaded successfully. Textures: {len(self._tex_placements)}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="q1q3utility",
        description="Utility to decompile Q3 maps to Q1 maps.\n",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"example:\n python {os.path.basename(__file__)} -b map.bsp -c q1q3tex2wad.csv -t ./textures",
    )
    parser.add_argument("-b", "--bsp", help="path to the bsp file, the map to decompile")
    parser.add_argument(
        "-c",
        "--csv",
        default="q1q3tex2wad.csv",
        help="path to the csv file, list of texture replacements",
    )
    parser.add_argument(
        "-m",
        "--map",
        help="path to the map file, the decompiled map (used to skip decompile step and rerun texture replacement)",
    )
    parser.add_argument(
        "-t",
        "--tex",
        default="textures",
        help="path to quake3/quake live textures, used to replace textures in the map",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=128,
        help="maximum size for the wad bmp image (default: 128)",
    )
    parser.add_argument(
        "--cpus",
        type=int,
        default=4,
        help="number of CPUs to use for texture replacement (default: 4)",
    )
    parser.add_argument(
        "--type",
        type=str,
        default="MIPTEX",
        choices=["LUMP", "QPIC", "MIPTEX"],
        help="list data type [default: MIPTEX]",
    )


    q1q3util = Q1Q3Util(parser.parse_args())
    q1q3util.run()
