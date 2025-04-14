package kr.goldenmine.chakbootbackend.util

import java.awt.image.BufferedImage
import java.io.ByteArrayInputStream
import javax.imageio.ImageIO

fun byteArrayToBufferedImage(bytes: ByteArray): BufferedImage {
    val inputStream = ByteArrayInputStream(bytes)
    return ImageIO.read(inputStream) ?: throw IllegalArgumentException("Invalid image byte array")
}

// 디렉토리 탈출 취약점 대비
fun isValidUUID(uuid: String): Boolean {
    val uuidRegex = Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
    return uuidRegex.matches(uuid)
}
