from io import BytesIO

import numpy
from generated.formats.nif import NifFile
# import imagemagick
from wand.image import Image
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
        elif format_type == "pixels":
            self.pixel_data = data[1]
            self.width = data[2]
            self.height = data[3]
        elif format_type == "png":
            # create stream
            self.fm = FileManipulator()
            self.fm.from_bytes(data)
            # get pixel data using imagemagick
            with Image(blob=data) as img:
                self.pixel_data = img.export_pixels()
                self.width = img.width
                self.height = img.height
        elif format_type == "dds":
            # create stream
            self.fm = FileManipulator()
            self.fm.from_bytes(data)
            # get pixel data using imagemagick (convert to png first)
            with Image(blob=data, format="dds") as img:
                self.pixel_data = img.export_pixels()
                self.width = img.width
                self.height = img.height
        else:
            raise ValueError("Invalid format_type")
        
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
                # get pixel data using imagemagick (convert to png first)
                with Image(blob=stream.getvalue(), format="dds") as img:
                    # convert pixels to bytes
                    self.pixel_data = bytes(img.export_pixels())
                    self.width = img.width
                    self.height = img.height
            else:
                raise ValueError("Invalid format")
        else:
            raise ValueError("Invalid platform. Only Wii is supported at the moment.")
        
    def get_png(self) -> bytes:

        """
        Returns the texture as a PNG.

        Args:
        None

        Returns:
        The texture as a PNG.
        """

        # get png usingg imagemagick
        with Image(width=self.width, height=self.height, format="RGBA", depth=8, blob=self.pixel_data) as img:
            return img.make_blob("png")
    
    def get_jpeg(self) -> bytes:

        """
        Returns the texture as a JPEG.

        Args:
        None

        Returns:
        The texture as a JPEG.
        """

        # get jpeg using imagemagick
        with Image(width=self.width, height=self.height, format="RGBA", depth=8, blob=self.pixel_data) as img:
            return img.make_blob("jpeg")
    
    def get_tga(self) -> bytes:

        """
        Returns the texture as a TGA.

        Args:
        None

        Returns:
        The texture as a TGA.
        """

        # get tga using imagemagick
        with Image(width=self.width, height=self.height, format="RGBA", depth=8, blob=self.pixel_data) as img:
            return img.make_blob("tga")
        