package kr.goldenmine.chakbootbackend.util

import java.awt.image.BufferedImage
import java.io.ByteArrayInputStream
import javax.imageio.ImageIO

fun byteArrayToBufferedImage(bytes: ByteArray): BufferedImage {
    val inputStream = ByteArrayInputStream(bytes)
    return ImageIO.read(inputStream) ?: throw IllegalArgumentException("Invalid image byte array")
}