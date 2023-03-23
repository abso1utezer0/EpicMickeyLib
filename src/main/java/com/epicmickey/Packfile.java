package com.epicmickey;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.Reader;
import java.util.Arrays;
import java.util.zip.*;

public class Packfile {
  // instance variables
  private String packfilePath = "";
  private String magic = "    ";
  private int version = 0;
  private int numFiles = 0;
  private int headerZero = 0;
  private int headerSize = 0;
  private int headerDataPointer = 0;
  private int stringPointer = 0;
  private int currentDataPosition = 0;
  private int currentHeaderPosition = 0;

  private int[] stringPartitionFolderPointers;
  private int[] stringPartitionFilePointers;

  private String[] containingFilePaths = new String[0];

  // file manipulator
  private FileManipulator fm;
  // rconsole
  private RConsole r = new RConsole();

  // constructor
  
  /**
   * Creates a new packfile object.
   * 
   * @param  packfilePath  Path to the packfile.
   * Should be the path to an existing packfile if
   * extracting or the path to the packfile to create
   * if creating a new packfile.
   */
  public Packfile(String packfilePath) throws FileNotFoundException {
    this.packfilePath = packfilePath;
    // create file manipulator
    fm = new FileManipulator(new File(this.packfilePath), "rw");
  }
  
  /**
  * Extracts the packfile from the packfile object's
  * <code>packfilePath</code> to
  * <code>extractionPath</code>.
  *
  * @param  extractionPath  Path to the extraction
  * directory.
  * @throws  IOException  If an I/O error occurs.
  */
  public void extract(String extractionPath) throws IOException {
    // check if the extraction path exists, if not, create it
    File extractionDir = new File(extractionPath);
    if (!extractionDir.exists()) {
      extractionDir.mkdirs();
    }
    // get header values
    getHeaderValues();
    // check if the header magic is correct
    if (!magic.equals(" KAP")) {
      r.vLog("Incorrect header magic '" + magic + "'! Aborting...");
      return;
    }
    r.vLog("Header magic: " + magic);
    // check if the header version is correct
    if (version != 2) {
      r.vLog("Incorrect header version '" + version + "'! Aborting...");
      return;
    }
    r.vLog("Header version: " + version);
    // check if the header zero is correct
    if (headerZero != 0) {
      r.vLog("Incorrect header zero '" + headerZero + "'! Aborting...");
      return;
    }
    r.vLog("Header zero: " + headerZero);
    r.vLog("Header size: " + headerSize);
    r.vLog("Data offset: " + headerDataPointer);
    r.vLog("Number of files: " + numFiles);
    // go to the header position
    try {
      fm.seek(currentHeaderPosition);
    } catch (IOException e) {
      r.vLog("Error seeking to header position! Aborting...");
      return;
    }
    r.vLog("Seeked to header position: " + currentHeaderPosition);
    for (int i = 0; i < numFiles; i++) {

      // get the real file size as a 4 byte int
      int realFileSize;
      try {
        realFileSize = fm.rInt();
      } catch (IOException e) {
        r.vLog("Error reading real file size of file number " + i + " Aborting...");
        return;
      }
      r.vLog("File " + i + " real file size: " + realFileSize);

      // get the compressed file size as a 4 byte int
      int compressedFileSize;
      try {
        compressedFileSize = fm.rInt();
      } catch (IOException e) {
        r.vLog("Error reading compressed file size of file number " + i + " Aborting...");
        return;
      }
      r.vLog("File " + i + " compressed file size: " + compressedFileSize);

      // get the aligned file size as a 4 byte int
      int alignedFileSize;
      try {
        alignedFileSize = fm.rInt();
      } catch (IOException e) {
        r.vLog("Error reading aligned file size of file number " + i + " Aborting...");
        return;
      }
      r.vLog("File " + i + " aligned file size: " + alignedFileSize);

      // check if the aligned file size is modulatable by 32
      if (alignedFileSize % 32 != 0) {
        r.vLog("Aligned file size of file number " + i + " is not modulatable by 32! Aborting...");
        // return;
      }

      // read the folder pointer as a 4 byte int
      int folderPointer;
      try {
        folderPointer = fm.rInt();
      } catch (IOException e) {
        r.vLog("Error reading folder pointer of file number " + i + " Aborting...");
        return;
      }
      r.vLog("File " + i + " folder pointer: " + folderPointer);

      // read the file extension as a 4 byte string
      String fileExtension;
      try {
        fileExtension = fm.rString(4);
      } catch (IOException e) {
        r.vLog("Error reading file extension of file number " + i + " Aborting...");
        return;
      }
      r.vLog("File " + i + " file extension: " + fileExtension);

      // read the file name pointer as a 4 byte int
      int fileNamePointer;
      try {
        fileNamePointer = fm.rInt();
      } catch (IOException e) {
        r.vLog("Error reading file name pointer of file number " + i + " Aborting...");
        return;
      }
      r.vLog("File " + i + " file name pointer: " + fileNamePointer);

      // add the string pointer to the folder name pointer and the file name pointer
      r.vLog("String pointer: " + stringPointer);
      folderPointer += stringPointer;
      r.vLog("Final folder name pointer: " + folderPointer);
      fileNamePointer += stringPointer;
      r.vLog("Final file name pointer: " + fileNamePointer);

      // set the current header position to the current position
      try {
        currentHeaderPosition = (int) fm.getFilePointer();
      } catch (IOException e) {
        r.vLog("Error getting current header position! Aborting...");
        return;
      }

      // go to the folder name pointer
      try {
        fm.seek(folderPointer);
      } catch (IOException e) {
        r.vLog("Error seeking to folder name pointer! Aborting...");
        return;
      }

      // read the folder name as a null terminated string
      String folderName;
      try {
        folderName = fm.rStringUntilNull();
      } catch (IOException e) {
        r.vLog("Error reading folder name! Aborting...");
        return;
      }

      // go to the file name pointer
      try {
        fm.seek(fileNamePointer);
      } catch (IOException e) {
        r.vLog("Error seeking to file name pointer! Aborting...");
        return;
      }

      // read the file name as a null terminated string
      String fileName;
      try {
        fileName = fm.rStringUntilNull();
      } catch (IOException e) {
        r.vLog("Error reading file name! Aborting...");
        return;
      }

      folderName += "/";

      // create the file path
      String filePath = extractionPath + folderName + fileName;

      // copy the containing file paths array to a temporary array
      String[] tempFilePaths = new String[containingFilePaths.length + 1];
      for (int j = 0; j < containingFilePaths.length; j++) {
        tempFilePaths[j] = containingFilePaths[j];
      }
      tempFilePaths[containingFilePaths.length] = filePath;
      containingFilePaths = tempFilePaths;

      // create the file
      File file = new File(filePath);
      // if the file exists, delete it and remake it
      if (file.exists()) {
        file.delete();
        try {
          file.createNewFile();
        } catch (IOException e) {
          r.vLog("Error creating file! Aborting...");
          return;
        }
      }

      // if the folders don't exist, create them
      if (!file.getParentFile().exists()) {
        file.getParentFile().mkdirs();
      }
      // create the filemanipulator
      FileManipulator fm2 = new FileManipulator(file, "rw");

      // go to the current data position
      try {
        fm.seek(currentDataPosition);
      } catch (IOException e) {
        r.vLog("Error seeking to current data position! Aborting...");
        fm2.close();
        return;
      }
      r.vLog("Current data position: " + currentDataPosition);

      // read the file data
      byte[] fileData;
      try {
        fileData = fm.rBytes(compressedFileSize);
      } catch (IOException e) {
        r.vLog("Error reading file data! Aborting...");
        fm2.close();
        return;
      }
      boolean quickAccess = true;
      // if the file is compressed, decompress it
      if (compressedFileSize != realFileSize) {
        try {
          quickAccess = false;
          // decompress the file data
          Inflater decompresser = new Inflater();
          decompresser.setInput(fileData);
          byte[] result = new byte[realFileSize];
          decompresser.inflate(result);
          decompresser.end();
          fileData = result;
        } catch (DataFormatException e) {
          r.vLog("Error decompressing file data! Aborting...");
          fm2.close();
          return;
        }

      }
      // write the file data to the file
      try {
        fm2.wBytes(fileData);
      } catch (IOException e) {
        r.vLog("Error writing file data! Aborting...");
        fm2.close();
        return;
      }
      // set the current data position to the aligned file size
      currentDataPosition += alignedFileSize;
      // close the filemanipulator
      fm2.close();
      // go to the next header position
      try {
        fm.seek(currentHeaderPosition);
      } catch (IOException e) {
        r.vLog("Error seeking to next header position! Aborting...");
        return;
      }
    }
    // vlog done
    r.vLog("Done!");
    // vlog output path
    r.vLog("Output path: " + extractionPath);
  }

  public String[] getContainingFilePaths() {
    return containingFilePaths;
  }

  public String assemblePathPartition(String[] paths) {
    String pathPartition = "";
    String currentFolder = "";
    int currentFolderPointer = 0;
    stringPartitionFolderPointers = new int[paths.length];
    stringPartitionFilePointers = new int[paths.length];
    for (int i = 0; i < paths.length; i++) {
      paths[i] = paths[i].replace("\\", "/");
      // split the path into parts split by forward slashes
      String[] splitPath = paths[i].split("/");
      // get the filename
      String filename = splitPath[splitPath.length - 1];
      // get the directory
      String directory = paths[i].replace(filename, "");
      // remove the last forward slash from the directory
      directory = directory.substring(0, directory.length() - 1);

      // if the directory is not the same as the current folder, append it to the path
      // partition
      if (!directory.equals(currentFolder)) {
        // update the current folder pointer
        currentFolderPointer = pathPartition.length();
        pathPartition += directory;
        currentFolder = directory;
        // write a null byte to the path partition
        pathPartition += (char) 0;
      }
      // add the folder name pointer to the array
      stringPartitionFolderPointers[i] = currentFolderPointer;
      // add the file name pointer to the array
      stringPartitionFilePointers[i] = pathPartition.length();
      // write the filename to the path partition
      pathPartition += filename;
      // write a null byte to the path partition
      pathPartition += (char) 0;

    }
    return pathPartition;
  }

  public void compress(String basePath, String[] filesToCompress) throws IOException {

    // delete the packfile if it exists
    File packfile = new File(packfilePath);
    if (packfile.exists()) {
      packfile.delete();
    }
    // create the packfile
    try {
      packfile.createNewFile();
    } catch (IOException e1) {
      // TODO Auto-generated catch block
      e1.printStackTrace();
    }

    // add the base path to the files to compress
    String[] tempFilesToCompress = new String[filesToCompress.length];
    for (int i = 0; i < filesToCompress.length; i++) {
      tempFilesToCompress[i] = filesToCompress[i];
    }
    filesToCompress = new String[tempFilesToCompress.length];
    for (int i = 0; i < tempFilesToCompress.length; i++) {
      filesToCompress[i] = basePath + tempFilesToCompress[i];
    }

    // check if the files to compress exist
    for (String fileToCompress : filesToCompress) {
      File file = new File(fileToCompress);
      if (!file.exists()) {
        r.vLog(fileToCompress + " does not exist! Skipping...");
        // remove the file path from the array
        filesToCompress = removeElement(filesToCompress, fileToCompress);
      }
    }

    // check if there are any files to compress
    if (filesToCompress.length == 0) {
      r.vLog("No files to compress! Aborting...");
      return;
    }

    // get paths at the relative position of the base path
    String[] relativePaths = new String[filesToCompress.length];
    for (int i = 0; i < filesToCompress.length; i++) {
      relativePaths[i] = filesToCompress[i].replace(basePath, "");
    }

    // assemble the path partition
    String pathPartition = assemblePathPartition(relativePaths);

    // get the number of files to compress
    numFiles = filesToCompress.length;

    // set the header magic
    magic = " KAP";
    // set the version
    version = 2;
    // set the header zero
    headerZero = 0;
    // set the header size
    headerSize = 32;
    // set header data pointer
    headerDataPointer = headerSize + pathPartition.length() + (numFiles * 24);
    // while the header data pointer is not aligned, add one to it
    while (headerDataPointer % 32 != 0) {
      headerDataPointer++;
    }

    // write the header magic
    try {
      fm.wString(magic);
    } catch (IOException e) {
      r.vLog("Error writing header magic! Aborting...");
      return;
    }

    // write the version
    try {
      fm.wInt(version);
    } catch (IOException e) {
      r.vLog("Error writing version! Aborting...");
      return;
    }

    // write the header zero
    try {
      fm.wInt(headerZero);
    } catch (IOException e) {
      r.vLog("Error writing header zero! Aborting...");
      return;
    }

    // write the header size
    try {
      fm.wInt(headerSize);
    } catch (IOException e) {
      r.vLog("Error writing header size! Aborting...");
      return;
    }
    // write the data offset
    try {
      fm.wInt(headerDataPointer - headerSize);
    } catch (IOException e) {
      r.vLog("Error writing data offset! Aborting...");
      return;
    }

    // go to the header size
    try {
      fm.seek(headerSize);
    } catch (IOException e) {
      r.vLog("Error seeking to header size! Aborting...");
      return;
    }

    // write the number of files
    try {
      fm.wInt(numFiles);
    } catch (IOException e) {
      r.vLog("Error writing number of files! Aborting...");
      return;
    }

    // set the current header position
    currentHeaderPosition = headerSize + 4;

    // set the string partition offset
    stringPointer = currentHeaderPosition + (numFiles * 24);

    // go to the string partition offset
    try {
      fm.seek(stringPointer);
    } catch (IOException e) {
      r.vLog("Error seeking to string partition offset! Aborting...");
      return;
    }

    // write the string partition
    try {
      fm.wString(pathPartition);
    } catch (IOException e) {
      r.vLog("Error writing string partition! Aborting...");
      return;
    }

    currentDataPosition = headerDataPointer;

    // go to the current header position
    try {
      fm.seek(currentHeaderPosition);
    } catch (IOException e) {
      r.vLog("Error seeking to current header position! Aborting...");
      return;
    }

    // loop through the files to compress
    for (int i = 0; i < numFiles; i++) {
      // create a new file manipilator for the current file
      FileManipulator fm2 = new FileManipulator(new File(filesToCompress[i]), "r");
      boolean quickAccess = false;
      // get the file extension
      String fileExtension = filesToCompress[i].substring(filesToCompress[i].lastIndexOf(".") + 1);
      // check if the file extension is a quick access file
      switch (fileExtension) {
        case "hkx":
        case "hkx_wii":
        case "hkw":
        case "hkw_wii":
        case "nif":
        case "nif_wii":
        case "kfm":
        case "kfm_wii":
        case "kf":
        case "kf_wii":
        case "lit":
        case "lit_cooked":
        case "bsq":
        case "dct":
          // set quick access to true
          quickAccess = true;
          break;
        default:
          // set quick access to false
          quickAccess = false;
          break;
      }
      // init string header file extension
      String stringHeaderFileExtension = "";
      switch (fileExtension.toLowerCase()) {
        case "hkx":
        case "hkx_wii":
          // go to offset 58 in the file and read an int
          try {
            fm2.seek(58);
          } catch (IOException e) {
            r.vLog("Error seeking to offset 58 in " + filesToCompress[i] + "! Aborting...");
            return;
          }
          int hkxType = 0;
          try {
            hkxType = fm2.rInt();
          } catch (IOException e) {
            r.vLog("Error reading int at offset 58 in " + filesToCompress[i] + "! Aborting...");
            return;
          }
          // check the hkx type
          switch (hkxType) {
            case 224:
              stringHeaderFileExtension = "HKB";
              break;
            case 144:
              stringHeaderFileExtension = "HKP";
              break;
            default:
              stringHeaderFileExtension = "HKX";
              break;
          }
          break;
        case "hkw":
        case "hkw_wii":
          stringHeaderFileExtension = "HKW";
          break;
        case "nif":
        case "nif_wii":
          stringHeaderFileExtension = "NIF";
          break;
        case "kfm":
        case "kfm_wii":
          stringHeaderFileExtension = "KFM";
          break;
        case "kf":
        case "kf_wii":
          stringHeaderFileExtension = "KF";
          break;
        case "bsq":
          stringHeaderFileExtension = "BSQ";
          break;
        case "lit_cooked":
          stringHeaderFileExtension = "LIT";
          break;
        case "gfx":
          stringHeaderFileExtension = "GFX";
          break;
        default:
          stringHeaderFileExtension = "";
          break;
      }
      // seek back to the start of the file
      try {
        fm2.seek(0);
      } catch (IOException e) {
        r.vLog("Error seeking to start of " + filesToCompress[i] + "! Aborting...");
        fm2.close();
        return;
      }
      // get the file data
      byte[] fileData;
      try {
        fileData = fm2.rBytes(fm2.getFileSize());
      } catch (IOException e) {
        r.vLog("Error getting file data! Aborting...");
        fm2.close();
        return;
      }
      // get the real file size
      int realFileSize;
      try {
        realFileSize = (int) fm2.getFileSize();
      } catch (IOException e) {
        r.vLog("Error getting real file size! Aborting...");
        fm2.close();
        return;
      }
      int compressedFileSize;
      // compress the file data if quick access is false
      if (!quickAccess) {
        // create deflater
        Deflater compressor = new Deflater();
        // set the input
        compressor.setInput(fileData);
        // finish the compression
        compressor.finish();
        // create a new byte array for the compressed data
        byte[] compressedData = new byte[realFileSize];
        // compress the data to fileData
        int compressedDataLength = compressor.deflate(compressedData);
        // cut the compressed data to the compressed data length
        compressedData = Arrays.copyOfRange(compressedData, 0, compressedDataLength);
        // set the file data to the compressed data
        fileData = compressedData;
        compressedFileSize = compressedDataLength;
      } else {
        compressedFileSize = realFileSize;
      }
      // vlog compressed file size
      r.vLog("Compressed file size: " + compressedFileSize);
      // set the compressed file size to the file data length
      // int compressedFileSize = fileData.length;
      // set the aligned file size to the compressed file size
      int alignedFileSize = compressedFileSize;
      // while the aligned file size is not modulo 32, add 1 to the aligned file size
      while (alignedFileSize % 32 != 0) {
        alignedFileSize++;
      }
      // write the real file size
      try {
        fm.wInt(realFileSize);
      } catch (IOException e) {
        r.vLog("Error writing real file size! Aborting...");
        fm2.close();
        return;
      }
      // write the compressed file size
      try {
        fm.wInt(compressedFileSize);
      } catch (IOException e) {
        r.vLog("Error writing compressed file size! Aborting...");
        fm2.close();
        return;
      }
      // write the aligned file size
      try {
        fm.wInt(alignedFileSize);
      } catch (IOException e) {
        r.vLog("Error writing aligned file size! Aborting...");
        fm2.close();
        return;
      }
      // write the string partition folder offset
      try {
        fm.wInt(stringPartitionFolderPointers[i]);
      } catch (IOException e) {
        r.vLog("Error writing string partition folder offset! Aborting...");
        fm2.close();
        return;
      }
      // write the string header file extension
      try {
        fm.wString(stringHeaderFileExtension);
      } catch (IOException e) {
        r.vLog("Error writing string header file extension! Aborting...");
        fm2.close();
        return;
      }
      // check if the header file extension is longer than 4 characters, if so,
      // throw an error
      if (stringHeaderFileExtension.length() > 4) {
        r.vLog("Error! Header file extension is longer than 4 characters! Aborting...");
        fm2.close();
        return;
      } else {
        if (stringHeaderFileExtension.length() <= 0) {
          try {
            fm.writeByte(0);
          } catch (IOException e) {
            r.vLog("Error writing padding! Aborting...");
            fm2.close();
            return;
          }
        }
        // go foward until position is a multiple of 4
        try {
          while (fm.getFilePointer() % 4 != 0) {
            try {
              fm.writeByte(0);
            } catch (IOException e) {
              r.vLog("Error writing padding! Aborting...");
              fm.close();
              return;
            }
          }
        } catch (IOException e) {
          // TODO Auto-generated catch block
          e.printStackTrace();
        }
      }

      // write the string partition file offset
      try {
        fm.wInt(stringPartitionFilePointers[i]);
      } catch (IOException e) {
        r.vLog("Error writing string partition file offset! Aborting...");
        fm2.close();
        return;
      }

      // set the current header position to the current file offset
      try {
        currentHeaderPosition = (int) fm.getFilePointer();
      } catch (IOException e) {
        r.vLog("Error getting current file offset! Aborting...");
        fm2.close();
        return;
      }

      // go to the current data position
      try {
        fm.seek(currentDataPosition);
      } catch (IOException e) {
        r.vLog("Error seeking to current data position! Aborting...");
        fm2.close();
        return;
      }

      // write the file data
      try {
        fm.wBytes(fileData);
      } catch (IOException e) {
        r.vLog("Error writing file data! Aborting...");
        fm2.close();
        return;
      }

      // add the aligned file size to the current data position
      currentDataPosition += alignedFileSize;
      int nullAmount = alignedFileSize - compressedFileSize;
      // write null bytes
      for (int j = 0; j < nullAmount; j++) {
        try {
          fm.writeByte(0);
        } catch (IOException e) {
          r.vLog("Error writing null bytes! Aborting...");
          fm2.close();
          return;
        }
      }

      // go to the current header position
      try {
        fm.seek(currentHeaderPosition);
      } catch (IOException e) {
        r.vLog("Error seeking to current header position! Aborting...");
        fm2.close();
        return;
      }

    }
    // vlog that the compression is complete
    r.vLog("Compression complete!");
  }

  private String[] removeElement(String[] filesToCompress, String fileToCompress) {
    // create new array
    String[] newArray = new String[filesToCompress.length - 1];
    // loop through the array
    for (int i = 0; i < filesToCompress.length; i++) {
      // check if the current element is the element to remove
      if (filesToCompress[i] != fileToCompress) {
        // add the element to the new array
        newArray[i] = filesToCompress[i];
      }
    }
    return newArray;
  }

  public String getHeaderMagic() throws IOException {
    // read the first 4 bytes of the file as a string and go back to the beginning
    fm.seek(0);
    String value = fm.rString(4);
    fm.seek(0);
    return value;
  }

  public int getHeaderVersion() throws IOException {
    // read the next 4 bytes of the file as an int and go back to the beginning
    fm.seek(4);
    int value = fm.rInt();
    fm.seek(0);
    return value;
  }

  
  public int getHeaderZero() throws IOException {
    // read the next 4 bytes of the file as an int and go back to the beginning
    fm.seek(8);
    int value = fm.rInt();
    fm.seek(0);
    return value;
  }
  
  /**
  * Get the size of the header in bytes.
  *
  * @return The size of the header in bytes.
  * @throws IOException If an I/O error occurs.
  */
  public int getHeaderSize() throws IOException {
    // read the next 4 bytes of the file as an int and go back to the beginning
    fm.seek(12);
    int value = fm.rInt();
    fm.seek(0);
    return value;
  }

  public int getHeaderDataPointer() throws IOException {
    // read the next 4 bytes of the file as an int and go back to the beginning
    fm.seek(16);
    int value = fm.rInt();
    fm.seek(0);
    return value;
  }

  /**
  * Gets the number of files in the packfile.
  *
  * @return The number of files in the packfile.
  * @throws IOException If an I/O error occurs.
  */
  public int getHeaderNumFiles() throws IOException {
    int offset = getHeaderSize();
    // read the next 4 bytes of the file as an int and go back to the beginning
    fm.seek(offset);
    r.vLog("Num File Offset: " + offset);
    int value = fm.rInt();
    fm.seek(0);
    return value;
  }
  
  /**
  * Closes the packfile stream. The stream cannot be
  * reopened upon closing.
  *
  * @throws IOException If an I/O error occurs.
  */
  public void close() throws IOException {
    fm.close();
    r.vLog("File closed!");
  }

  /**
  * Gets all the header values in the packfile
  * to get ready for extraction.
  */
  private void getHeaderValues() {
    try {
      magic = getHeaderMagic();
      version = getHeaderVersion();
      headerZero = getHeaderZero();
      headerSize = getHeaderSize();
      headerDataPointer = getHeaderDataPointer();
      headerDataPointer += headerSize;
      currentDataPosition = headerDataPointer;
      numFiles = getHeaderNumFiles();
      stringPointer = (numFiles * 24) + headerSize + 4;
      currentHeaderPosition = headerSize + 4;
    } catch (IOException e) {
      e.printStackTrace();
    }
  }
}
