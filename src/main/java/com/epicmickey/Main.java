package com.epicmickey;

import java.io.FileNotFoundException;
import java.io.IOException;

public class Main {
  public static void main(String[] args) throws FileNotFoundException, IOException {
    Scene bin = new Scene("eb_villagetest.bin");
    bin.decompile("eb_villagetest.bin.json");
    String[] referencedPaths = bin.getReferencedPaths();
    for (String referencedPath : referencedPaths) {
      System.out.println(referencedPath);
    }
  }
}