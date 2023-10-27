from io import BytesIO
import math

import numpy
from generated.formats.nif import NifFile
# import pillow
import PIL
from epicmickeylib.internal.filemanipulator import FileManipulator
from generated.formats.nif.enums.PlatformID import PlatformID
from generated.formats.nif.enums.PixelFormat import PixelFormat

class Texture:
    fm = None
    pixel_data = None
    width = None
    height = None

    def __init__(self, data, format_type="binary") -> None:

        """
        Initializes a Texture object.

        Args:
        - data: the data to be used to initialize the object
        - format_type: the format of the data (binary, pixels, png, dds)

        Returns:
        None
        """

        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data)
            self.decompile()
        elif format_type == "raw":
            self.pixel_data = data[1]
            self.width = data[2]
            self.height = data[3]
        elif format_type == "png":
            # create stream
            self.fm = FileManipulator()
            self.fm.from_bytes(data)
            # get pixel data using pillow
            with PIL.Image.open(BytesIO(data)) as img:
                # get pixel data
                self.pixel_data = img.tobytes()
                self.width = img.width
                self.height = img.height
        elif format_type == "dds":
            # create stream
            self.fm = FileManipulator()
            self.fm.from_bytes(data)
            # get pixel data using pillow (convert to png first)
            with PIL.Image.open(BytesIO(data)) as img:
                # get pixel data
                self.pixel_data = img.tobytes()
                self.width = img.width
                self.height = img.height
        elif format_type == "tga":
            # create stream
            self.fm = FileManipulator()
            self.fm.from_bytes(data)
            # get pixel data using pillow (convert to png first)
            with PIL.Image.open(BytesIO(data)) as img:
                # get pixel data
                self.pixel_data = img.tobytes()
                self.width = img.width
                self.height = img.height
        else:
            raise ValueError("Invalid format_type")
    
    def untile_pixels(self, pixels: list, width: int) -> list:
        rearranged_pixels = []
        num = width * 4
        for i in range(0, len(pixels), num):
            for j in range(0, 16, 4):
                for k in range(i+j, i+num+j, 16):
                    pixels_to_add = pixels[k:k+4]
                    for pixel in pixels_to_add:
                        rearranged_pixels.append(pixel)
        return rearranged_pixels
        
    def decompile(self) -> None:

        """
        Decompiles a NIF texture file.

        Args:
        None

        Returns:
        None
        """

        binary_data = self.fm.get_bytes()
        # create empty stream
        stream = BytesIO(binary_data)
        # create NIF object
        nif = NifFile.from_stream(stream)

        format = None
        pixel_data = None
        width = None
        height = None
        platform = None
        bits_per_pixel = None
        tex_block = None
        
        for block in nif.blocks:
            if block.__class__.__name__ == "NiPersistentSrcTextureRendererData":
                tex_block = block
                format = block.pixel_format
                pixel_data = block.pixel_data
                largest_mipmap = block.mipmaps[0]
                width = largest_mipmap.width
                height = largest_mipmap.height
                platform = block.platform
                bits_per_pixel = block.bits_per_pixel
        print(tex_block)
        if platform == PlatformID.WII:
            if format == PixelFormat.FMT_DXT1:

                bytes_per_chunk = width * 4
                chunks = []
                crop = (width * height) // 2
                data_to_use = tex_block.pixel_data[:crop]
                for i in range(0, len(data_to_use), bytes_per_chunk):
                    chunks.append(data_to_use[i:i+bytes_per_chunk])
                new_bytes_to_use = b""
                for chunk in chunks:
                    # split the chunk into rows, each row is 16 bytes
                    rows = []
                    for i in range(0, len(chunk), 16):
                        rows.append(chunk[i:i+16])
                    group_one = []
                    group_two = []
                    for i in range(0, len(rows), 2):
                        group_one.append(rows[i])
                        if i + 1 < len(rows):
                            group_two.append(rows[i+1])
                    final_rows = []
                    for i in range(0, len(group_one)):
                        final_rows.append(group_one[i])
                    for i in range(0, len(group_two)):
                        final_rows.append(group_two[i])
                    for row in final_rows:
                        for byte in row:
                            new_bytes_to_use += bytes([byte])
                # overwrite the old pixel data from the beginning
                for i in range(len(new_bytes_to_use)):
                    tex_block.pixel_data[i] = new_bytes_to_use[i]

                # run through every 8 bytes
                for i in range(0, len(tex_block.pixel_data), 8):
                    chunk = tex_block.pixel_data[i:i+8]
                    new_chunk = b""
                    new_chunk += chunk[1]
                    new_chunk += chunk[0]
                    new_chunk += chunk[3]
                    new_chunk += chunk[2]
                    nibble_map = {
                        "e": "b",
                        "d": "7",
                        "c": "3",
                        "b": "e",
                        "9": "6",
                        "8": "2",
                        "7": "d",
                        "6": "9",
                        "4": "1",
                        "3": "c",
                        "2": "8",
                        "1": "4"
                    }
                    # for the last 4 bytes, reverse them (e.g. 0x0F -> 0xF0)
                    for j in range(4, 8):
                        # reverse the byte
                        byte = chunk[j]
                        hex_byte = hex(byte)[2:]
                        if len(hex_byte) == 1:
                            hex_byte = "0" + hex_byte
                        first_nibble = hex_byte[0]
                        second_nibble = hex_byte[1]
                        new_byte = second_nibble + first_nibble
                        # replace the nibbles if they need to be replaced
                        for k in range(len(new_byte)):
                            nibble = new_byte[k]
                            if nibble in nibble_map:
                                new_byte = new_byte[:k] + nibble_map[nibble] + new_byte[k+1:]
                        # convert the byte back to an int
                        new_byte = int(new_byte, 16)
                        new_chunk += bytes([new_byte])
 
                    # replace the chunk
                    for j in range(8):
                        tex_block.pixel_data[i+j] = new_chunk[j]
                
                # create empty stream
                stream = BytesIO()
                tex_block.save_as_dds(stream)
                # get pixel data using pillow
                with PIL.Image.open(stream) as img:
                    # convert to RGBA
                    img = img.convert("RGBA")
                    # get pixel data
                    self.pixel_data = img.tobytes()
                    self.width = img.width
                    self.height = img.height
            elif format == PixelFormat.FMT_RGBA:
                print(tex_block.bytes_per_pixel)
                if bits_per_pixel == 16:
                    # crop the pixel data
                    crop = (width * height) * 2
                    pixel_data = pixel_data[:crop]
                    # add alpha channel
                    pixels = []
                    def bits_to_channel(bits: list) -> int:
                        binary = ""
                        for bit in bits:
                            binary += str(bit)
                        multiply_by = 2**(8-len(bits))
                        return int(binary, 2) * multiply_by
                    for i in range(0, len(pixel_data), 2):
                        pixel_bytes = pixel_data[i:i+2]
                        # convert to binary list (0 or 1)
                        binary_list = []
                        for byte in pixel_bytes:
                            binary = bin(byte)[2:]
                            # pad with 0s
                            while len(binary) < 8:
                                binary = "0" + binary
                            for bit in binary:
                                binary_list.append(int(bit))
                        alpha = 0
                        red = 0
                        green = 0
                        blue = 0

                        read_alpha = False
                        if binary_list[0] == 0:
                            read_alpha = True
                        if read_alpha:
                            alpha = bits_to_channel(binary_list[1:4])
                            red = bits_to_channel(binary_list[4:8])
                            green = bits_to_channel(binary_list[8:12])
                            blue = bits_to_channel(binary_list[12:16])
                        else:
                            alpha = 255
                            red = bits_to_channel(binary_list[1:6])
                            green = bits_to_channel(binary_list[6:11])
                            blue = bits_to_channel(binary_list[11:16])
                        pixels.append([red, green, blue, alpha])
                    new_pixel_data = b""
                    pixels = self.untile_pixels(pixels, width)
                    for pixel in pixels:
                        for byte in pixel:
                            new_pixel_data += bytes([byte])
                    self.pixel_data = new_pixel_data
                    self.width = width
                    self.height = height
                elif bits_per_pixel == 32:
                
                    # crop the pixel data
                    crop = (width * height) * 4
                    pixel_data = pixel_data[:crop]

                    tiles = []
                    # each tile is 64 bytes
                    for i in range(0, len(pixel_data), 64):
                        first_half = pixel_data[i:i+32]
                        second_half = pixel_data[i+32:i+64]

                        tile_data = []

                        alpha_values = []
                        red_values = []
                        green_values = []
                        blue_values = []
                        # alphas
                        for j in range(0, len(first_half), 2):
                            alpha_values.append(first_half[j])
                        # reds
                        for j in range(1, len(first_half), 2):
                            red_values.append(first_half[j])
                        # greens
                        for j in range(0, len(second_half), 2):
                            green_values.append(second_half[j])
                        # blues
                        for j in range(1, len(second_half), 2):
                            blue_values.append(second_half[j])
                        
                        # create the tile data
                        for j in range(len(alpha_values)):
                            tile_data.append(red_values[j])
                            tile_data.append(green_values[j])
                            tile_data.append(blue_values[j])
                            tile_data.append(alpha_values[j])
                        
                        tiles.append(tile_data)
                    
                    new_pixel_data = b""

                    for tile in tiles:
                        for byte in tile:
                            new_pixel_data += bytes([byte])

                    pixels = []
                    for i in range(0, len(new_pixel_data), 4):
                        pixels.append(new_pixel_data[i:i+4])
                    
                    pixels = self.untile_pixels(pixels, width)

                    new_pixel_data = b""
                    for pixel in pixels:
                        for byte in pixel:
                            new_pixel_data += bytes([byte])

                    self.pixel_data = new_pixel_data
                    self.width = width
                    self.height = height
            elif format == PixelFormat.FMT_RGB:
                # crop the pixel data
                crop = (width * height) * 3
                pixel_data = pixel_data[:crop]
                # add alpha channel
                new_pixel_data = b""
                for i in range(0, len(pixel_data), 3):
                    new_pixel_data += pixel_data[i:i+3]
                    new_pixel_data += bytes([255])
                self.pixel_data = new_pixel_data
                self.width = width
                self.height = height
            elif format == PixelFormat.FMT_2CH:
                pixels = []
                for i in range(0, len(pixel_data), 2):
                    pixel = []
                    # alpha is the first byte
                    alpha = pixel_data[i]
                    # intensity is the second byte
                    intensity = pixel_data[i+1]
                    for j in range(3):
                        pixel.append(intensity)
                    pixel.append(alpha)
                    print(pixel)
                    pixels.append(pixel)
                # crop
                crop = (width * height)
                pixels = pixels[:crop]
                pixels = self.untile_pixels(pixels, width)
                # create pixel data
                new_pixel_data = b""
                for pixel in pixels:
                    for byte in pixel:
                        new_pixel_data += bytes([byte])
                self.pixel_data = new_pixel_data
                self.width = width
                self.height = height
            elif format == PixelFormat.FMT_1CH:
                pixels = []
                if bits_per_pixel == 8:
                    # 2ch but without alpha (1 byte per pixel)
                    for i in range(len(pixel_data)):
                        pixel = []
                        # intensity is the byte
                        intensity = pixel_data[i]
                        for j in range(4):
                            pixel.append(intensity)
                        pixels.append(pixel)
                elif bits_per_pixel == 4:
                    for i in range(0, len(pixel_data), 2):
                        # split byte into two nibbles
                        byte = pixel_data[i]
                        hex_byte = hex(byte)[2:]
                        if len(hex_byte) == 1:
                            hex_byte = "0" + hex_byte
                        first_nibble = bytes.fromhex(hex_byte[0] + hex_byte[0])
                        second_nibble = bytes.fromhex(hex_byte[1] + hex_byte[1])
                        for nibble in [first_nibble, second_nibble]:
                            pixel = []
                            # intensity is the nibble
                            intensity = nibble[0]
                            for j in range(4):
                                pixel.append(intensity)
                            pixels.append(pixel)
                else:
                    raise ValueError(f"Invalid bits per pixel '{bits_per_pixel}' for format '{format}'. Only 8 and 4 are supported at the moment.")
                # crop
                crop = (width * height)
                pixels = pixels[:crop]

                pixels = self.untile_pixels(pixels, width)
                # create pixel data
                new_pixel_data = b""
                for pixel in pixels:
                    for byte in pixel:
                        new_pixel_data += bytes([byte])
                self.pixel_data = new_pixel_data
                self.width = width
                self.height = height
            else:
                raise ValueError(f"Invalid format '{format}'. Only DXT1 is supported at the moment.")
        else:
            raise ValueError(f"Invalid platform '{platform}'. Only Wii is supported at the moment.")
        
    def get_png(self) -> bytes:

        """
        Returns the texture as a PNG.

        Args:
        None

        Returns:
        The texture as a PNG.
        """

        # get png
        with PIL.Image.frombytes("RGBA", (self.width, self.height), self.pixel_data) as img:
            with BytesIO() as stream:
                img.save(stream, format="png")
                return stream.getvalue()
    
    def get_jpeg(self, quality: int = 100) -> bytes:
        

        """
        Returns the texture as a JPEG.

        Args:
        None

        Returns:
        The texture as a JPEG.
        """

        # get jpeg using pillow
        with PIL.Image.frombytes("RGBA", (self.width, self.height), self.pixel_data) as img:
            # convert to jpeg
            img = img.convert("RGB")
            with BytesIO() as stream:
                img.save(stream, format="jpeg", quality=quality)
                return stream.getvalue()
    
    def get_tga(self) -> bytes:

        """
        Returns the texture as a TGA.

        Args:
        None

        Returns:
        The texture as a TGA.
        """

        # get tga using pillow
        with PIL.Image.frombytes("RGBA", (self.width, self.height), self.pixel_data) as img:
            with BytesIO() as stream:
                img.save(stream, format="tga")
                return stream.getvalue()