package com.epicmickey;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import org.json.JSONObject;

public class CLB {
  private String clbPath;
  private String jsonPath;
  private FileManipulator fm;

  public CLB(String path) throws FileNotFoundException {
    if (path.endsWith(".clb")) {
      clbPath = path;
      jsonPath = clbPath + ".json";

    } else if (path.endsWith(".clb.json")) {
      clbPath = path.replace(".json", "");
      jsonPath = path;
    }
    File f = new File(clbPath);
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

  public void decompile() throws FileNotFoundException, IOException {
    decompile(jsonPath);
  }

  public void decompile(String outputPath) throws FileNotFoundException, IOException {
    File f = new File(outputPath);

    if (f.exists()) {
      f.delete();
    }
    f.createNewFile();

    JSONObject json = new JSONObject();
    JSONObject general = new JSONObject();
    JSONObject extras = new JSONObject();

    // move forward 4 bytes
    fm.seekForward(4);

    int basicCollectibleCount = fm.rInt();

    int i = 0;
    while (i < basicCollectibleCount) {

      String type = getNextString();

      String name = getNextString();

      String icon = getNextString();

      JSONObject collectible = new JSONObject();
      collectible.put("type", type);
      collectible.put("icon", icon);

      general.put(name, collectible);

      alignTo(4);
      i++;
    }

    int extrasCollectibleCount = fm.rInt();

    i = 0;
    while (i < extrasCollectibleCount) {
      String type = getNextString();
      String name = getNextString();
      String icon = getNextString();
      String file = getNextString();

      JSONObject collectible = new JSONObject();

      collectible.put("type", type);
      collectible.put("icon", icon);
      collectible.put("file", file);

      extras.put(name, collectible);

      alignTo(4);
      i++;
    }

    json.put("general", general);
    json.put("extras", extras);

    FileManipulator jsonFM = new FileManipulator(f, "rw");
    jsonFM.wString(json.toString(2));
    jsonFM.close();

  }

}