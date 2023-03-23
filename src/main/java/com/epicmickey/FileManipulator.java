package com.epicmickey;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.channels.FileChannel;

public class FileManipulator extends RandomAccessFile{

    private boolean littleEndian = false;

    public FileManipulator(File file, String mode) throws FileNotFoundException {
        super(file, mode);
    }

    public void readAsLittleEndian(boolean bool) {
        littleEndian = bool;
    }
    public int rInt() throws IOException {
        if (littleEndian) {
            return Integer.reverseBytes(super.readInt());
        } else {
            return super.readInt();
        }
    }
    public int rInt(int len) throws IOException {
        int i = 0;
        for (int j = 0; j < len; j++) {
            i += super.readByte() << (j * 8);
        }
        if (littleEndian) {
            return Integer.reverseBytes(i);
        } else {
            return i;
        }
    }
    public short rShort() throws IOException {
        if (littleEndian) {
            return Short.reverseBytes(super.readShort());
        } else {
            return super.readShort();
        }
    }
    public long rLong() throws IOException {
        if (littleEndian) {
            return Long.reverseBytes(super.readLong());
        } else {
            return super.readLong();
        }
    }
    public float rFloat() throws IOException {
        if (littleEndian) {
            return Float.intBitsToFloat(Integer.reverseBytes(super.readInt()));
        } else {
            return super.readFloat();
        }
    }
    public double rDouble() throws IOException {
        if (littleEndian) {
            return Double.longBitsToDouble(Long.reverseBytes(super.readLong()));
        } else {
            return super.readDouble();
        }
    }
    public String rString(int length) throws IOException {
        byte[] bytes = new byte[length];
        super.read(bytes);
        return new String(bytes);
    }
    public String rStringUntilNull() throws IOException {
        StringBuilder sb = new StringBuilder();
        byte b;
        while ((b = super.readByte()) != 0) {
            sb.append((char) b);
        }
        return sb.toString();
    }
    public byte[] rBytes(int length) throws IOException {
        byte[] bytes = new byte[length];
        super.read(bytes);
        return bytes;
    }
    public void wInt(int i) throws IOException {
        if (littleEndian) {
            super.writeInt(Integer.reverseBytes(i));
        } else {
            super.writeInt(i);
        }
    }
    public void wShort(short s) throws IOException {
        if (littleEndian) {
            super.writeShort(Short.reverseBytes(s));
        } else {
            super.writeShort(s);
        }
    }
    public void wLong(long l) throws IOException {
        if (littleEndian) {
            super.writeLong(Long.reverseBytes(l));
        } else {
            super.writeLong(l);
        }
    }
    public void wFloat(float f) throws IOException {
        if (littleEndian) {
            super.writeInt(Integer.reverseBytes(Float.floatToIntBits(f)));
        } else {
            super.writeFloat(f);
        }
    }
    public void wDouble(double d) throws IOException {
        if (littleEndian) {
            super.writeLong(Long.reverseBytes(Double.doubleToLongBits(d)));
        } else {
            super.writeDouble(d);
        }
    }
    public void wString(String s) throws IOException {
        super.write(s.getBytes());
    }
    public void wBytes(byte[] bytes) throws IOException {
        super.write(bytes);
    }
    public int getFileSize() throws IOException {
        return (int) super.length();
    }
    public void seekForward(int i) throws IOException {
        super.seek(super.getFilePointer() + i);
    }

}
