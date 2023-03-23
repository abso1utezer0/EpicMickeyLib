package com.epicmickey;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import org.json.JSONObject;
import org.json.JSONException;
import org.json.JSONArray;
import java.util.ArrayList;
import java.io.BufferedReader;
import java.io.FileReader;

public class Part {
  private String[] lines;
  private String[] files;
  
  public Part(String[] lines) {
    ArrayList<String> files = new ArrayList<String>();
    this.lines = lines;
    for (String line : lines) {
      // split line at "//"
      String[] parts = line.split("//");
      line = parts[0];
      if (!line.isBlank()) {
        files.add(line);
      }
    }
    this.files = files.toArray(new String[files.size()]);
  }
  public Part(File file) throws FileNotFoundException {
    String path = file.getAbsolutePath();
    this(path)
  }
  public Part(String path) {
    // get the lines of the text file
    ArrayList<String> lines = new ArrayList<String>();
    BufferedReader reader = new BufferedReader(new FileReader(path));
    String line = reader.readLine();

		while (line != null) {
			lines.add(line);
			// read next line
			line = reader.readLine();
		}
    reader.close();
    this(lines.toArray(new String[lines.size()]));
  }
  public String[] getLines() {
    return lines;
  )
  public ArrayList<String> getLinesList() {
    ArrayList<String> lines = new ArrayList<String>();
    for (String line : this.lines) {
      lines.add(line);
    }
    return lines;
  }
  public String[] getPaths() {
    return files;
  }
  public ArrayList<String> getPathsList() {
    ArrayList<String> paths = new ArrayList<String>();
    for (String file : this.files) {
      paths.add(file);
    }
    return paths;
  }
}