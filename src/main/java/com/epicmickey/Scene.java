package com.epicmickey;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import org.json.JSONObject;
import org.json.JSONException;
import org.json.JSONArray;
import java.util.ArrayList;

public class Scene {
  private String binPath;
  private String jsonPath;
  private FileManipulator fm;

  public Scene(String path) throws FileNotFoundException {
    if (path.endsWith(".bin")) {
      binPath = path;
      jsonPath = binPath + ".json";

    } else if (path.endsWith(".bin.json")) {
      binPath = path.replace(".json", "");
      jsonPath = path;
    }
    File f = new File(binPath);
    fm = new FileManipulator(f, "rw");
  }

  private void alignTo(int alignment) throws FileNotFoundException, IOException {
    while (fm.getFilePointer() % alignment != 0) {
      fm.seekForward(1);
    }
  }

  private String getNextString() throws FileNotFoundException, IOException {
    alignTo(4);
    fm.seekForward(2);
    String string = fm.rStringUntilNull();
    return string;
  }
  public String[] getReferencedPaths() throws FileNotFoundException, IOException {
    String[] foldersToCheck = {
      "..",
      ".",
      "environments",
      "palettes",
      "skinnedprops",
      "movies",
      "scenedesigner",
      "localize",
      "characters",
      "handheld",
      "gameobjects",
      "levels",
      "effects",
      "apprentice",
      "igcs",
      "hudelements"
    };
    return getReferencedPaths(foldersToCheck);
  }
  public String[] getReferencedPaths(String[] foldersToCheck) throws FileNotFoundException, IOException {
    ArrayList<String> referencedPaths = new ArrayList<String>();
    
    for (String folderToCheck : foldersToCheck) {
      fm.seek(0);
      folderToCheck = folderToCheck.replace("\\", "/");
      folderToCheck = folderToCheck.toLowerCase()
      int stringPartitionSize = fm.rInt() - 4;
      while (fm.getFilePointer() < stringPartitionSize) {
        String string = getNextString();
        if (string.startsWith(folderToCheck + "/")) {
          referencedPaths.add(string);
        }
      }
    }
    fm.seek(0);
    return referencedPaths.toArray(new String[referencedPaths.size()]);
  }
    

  public void decompile() throws FileNotFoundException, IOException {
    decompile(jsonPath);
  }

  public void decompile(String outputPath) throws FileNotFoundException, IOException {
    File f = new File(outputPath);

    if (f.exists()) {
      f.delete();
    }
    f.createNewFile();

    int stringPartitionSize = fm.rInt() - 4;

    JSONObject json = new JSONObject();

    JSONArray strings = new JSONArray();

    while (fm.getFilePointer() < stringPartitionSize) {
      String string = getNextString();
      strings.put(string);
    }
    json.put("strings", strings);

    // read the rest of the file

    byte[] dataBytes = fm.rBytes(fm.getFileSize() - (int) fm.getFilePointer());

    // convert the bytes to hex
    JSONArray data = new JSONArray();
    for (byte b : dataBytes) {
      data.put(String.format("%02X ", b).replace(" ", ""));
    }

    json.put("data", data);

    FileManipulator jsonFM = new FileManipulator(f, "rw");
    jsonFM.wString(json.toString(2));
    jsonFM.close();

    fm.seek(0);

  }

}