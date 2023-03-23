package com.epicmickey;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import org.json.*;
import org.json.JSONObject;

public class Dict {
  private String filePath;
  private FileManipulator fm;
  private boolean binary = false;

  public Dict(String path) throws FileNotFoundException {
    filePath = path;
    if (path.endsWith(".dct")) {
      fm = new FileManipulator(new File(path), "rw");
      binary = true;
    }
  }

  public Dict(File f) throws FileNotFoundException {
    filePath = f.getAbsolutePath();
    fm = new FileManipulator(f, "rw");
    binary = true;
  }

  public void decompile(String path) throws IOException {
    if (!binary) {
      System.out.println(
          "Provided file cannot be decompiled as it is already in a JSON format. Please provide a DCT file.");
      return;
    }
    fm.readAsLittleEndian(true);
    String magic = fm.rString(4);
    if (!magic.equals("DICT")) {
      System.out.println(
          "Invalid DCT header magic '" + magic + "'.");
    }
    int version1 = fm.rInt();
    int translationRevision = fm.rInt();
    int version2 = fm.rInt();
    if (version1 != 8192) {
      System.out.println(
          "Invalid version1 '" + version1 + "'");
      return;
    }
    if (translationRevision == 0) {
      System.out.print(
          "Invalid translation revision number.");
      return;
    }
    if (version2 != 19) {
      System.out.println(
          "Invalid version2 '" + version2 + "'");
      return;
    }
    int lineCount = fm.rInt();
    if (lineCount == 0) {
      System.out.println(
          "No lines to decompile");
      return;
    }
    fm.seekForward(4);
    int footerOffset = (int) fm.getFilePointer() + fm.rInt() + 9;
    fm.seekForward(4);

    JSONObject json = new JSONObject();
    JSONObject lines = new JSONObject();
    JSONObject footer = new JSONObject();

    json.put("translation_revision", translationRevision);

    int currentDataOffset = (int) fm.getFilePointer();
    int emptyLines = 0;

    for (int i = 0; i < lineCount; i++) {
      JSONObject lineData = new JSONObject();
      // line id is 4 bytes hex
      String lineID = Integer.toHexString(fm.rInt());

      if (lineID.equals("0")) {
        lines.put("empty_line_" + emptyLines, "");
        emptyLines++;
        fm.seekForward(8);
        continue;
      }
      // if hex is less than 8 characters, add 0s to the front
      while (lineID.length() < 8) {
        lineID = "0" + lineID;
      }
      String firstTwo = lineID.substring(0, 2);
      String secondTwo = lineID.substring(2, 4);
      String thirdTwo = lineID.substring(4, 6);
      String fourthTwo = lineID.substring(6, 8);
      lineID = fourthTwo + thirdTwo + secondTwo + firstTwo;
      // line offset is 4 bytes int
      int lineOffset = (int) fm.getFilePointer() + fm.rInt() + 1;
      int lineZero = fm.rInt();
      currentDataOffset = (int) fm.getFilePointer();
      fm.seek(lineOffset);
      String line = fm.rStringUntilNull();
      lines.put(lineID, line);
      fm.seek(currentDataOffset);

    }
    // reverse the order of the lines
    JSONObject reversedLines = new JSONObject();
    for (int i = lines.length() - 1; i >= 0; i--) {
      reversedLines.put(lines.names().getString(i), lines.get(lines.names().getString(i)));
    }
    lines = reversedLines;
    while (fm.getFilePointer() < footerOffset) {
      int footerLineOffset = (int) fm.getFilePointer() + fm.rInt() + 1;
      int footerLineID = fm.rInt();
      currentDataOffset = (int) fm.getFilePointer();
      fm.seek(footerLineOffset);
      String line = fm.rStringUntilNull();
      footer.put(line, footerLineID);
      fm.seek(currentDataOffset);
    }
    json.put("footer", footer);
    json.put("lines", lines);

    System.out.println(json);
    // if file exists, delete it
    File f = new File(path);
    if (f.exists()) {
      f.delete();
    }
    // write to file
    FileManipulator fm2 = new FileManipulator(f, "rw");
    fm2.writeChars(json.toString(4));
    fm2.close();
  }

  public void compile(String path) throws JSONException, IOException {
    // get the json file from filePath
    File jsonFile = new File(filePath);
    if (!jsonFile.exists()) {
      System.out.println(
          "JSON file does not exist.");
      return;
    }
    FileManipulator jsonFM = new FileManipulator(jsonFile, "r");
    // read the json data
    JSONObject json = new JSONObject(jsonFM.rString((int) jsonFM.length()));
    jsonFM.close();
    // get the translation revision
    int translationRevision = json.getInt("translation_revision");
    // get the footer
    JSONObject footer = json.getJSONObject("footer");
    // get the lines
    JSONObject lines = json.getJSONObject("lines");
    // create the new dct file
    File dctFile = new File(path);
    if (dctFile.exists()) {
      dctFile.delete();
    }
    FileManipulator fm = new FileManipulator(dctFile, "rw");
    fm.readAsLittleEndian(true);
    fm.writeChars("DICT");
    fm.writeInt(8192);
    fm.writeInt(translationRevision);
    fm.writeInt(19);
    fm.writeInt(lines.length());
    fm.writeInt(1);
    int endOffset = (lines.length() * 12) + (footer.length() * 8) - 1;
    fm.writeInt(endOffset);
    fm.writeInt(1);
    int currentDataOffset = (int) fm.getFilePointer();
    int currentLineOffset = endOffset + 50;
    // seek to current line offset
    fm.seek(currentLineOffset);
    // write null byte
    fm.writeByte(0);
    // seek to current data offset
    fm.seek(currentDataOffset);
    // write the lines
    for (int i = 0; i < lines.length(); i++) {
      // get the id
      String id = lines.names().getString(i);
      // get the line
      String line = lines.getString(id);
      if (id.startsWith("empty_line_", 0)) {
        fm.writeInt(0);
        fm.writeInt(0);
        fm.writeInt(0);
        continue;
      }
      // write the id
      fm.writeInt(Integer.parseInt(id, 16));
      // write the offset
      fm.writeInt(currentLineOffset - (int) fm.getFilePointer() - 1);
    }
  }

}