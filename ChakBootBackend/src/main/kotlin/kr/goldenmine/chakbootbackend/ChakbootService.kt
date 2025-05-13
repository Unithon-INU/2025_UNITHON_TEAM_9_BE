package kr.goldenmine.chakbootbackend

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.compression.*
import io.ktor.client.request.forms.*
import io.ktor.client.statement.*
import io.ktor.http.*
import jakarta.annotation.PostConstruct
import kotlinx.coroutines.runBlocking
import kr.goldenmine.chakbootbackend.util.isValidUUID
import org.apache.coyote.BadRequestException
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import java.awt.Graphics2D
import java.awt.geom.AffineTransform
import java.awt.image.BufferedImage
import java.io.ByteArrayOutputStream
import java.io.File
import java.util.*
import javax.imageio.ImageIO

@Service
class ChakbootService(
    @Value("\${app.image_path}") private val imagePath: String,

    @Value("\${ftp.file.path}")
    private val ftpFilePath: String

) {
    private val logger: Logger = LoggerFactory.getLogger(ChakbootService::class.java)

    fun inferenceImage(img1: MultipartFile, img2: MultipartFile): ByteArray {
        val ktorClient = HttpClient(CIO) {
            install(ContentEncoding) {
                gzip() // Enable Gzip handling explicitly
            }
            install(HttpTimeout) {
                requestTimeoutMillis = 60_000 // 60초
                connectTimeoutMillis = 20_000
                socketTimeoutMillis = 60_000
            }
        }
        val img1Bytes = img1.bytes
        val img2Bytes = img2.bytes

//        return img1Bytes
        val result: ByteArray
        runBlocking {
            val response = ktorClient.submitFormWithBinaryData(
                url = "http://localhost:8086/predict/",
                formData = formData {
                    append("img1", img1Bytes, Headers.build {
                        append(HttpHeaders.ContentType, "image/png")
                        append(HttpHeaders.ContentDisposition, "filename=\"img1.png\"")
                    })
                    append("img2", img2Bytes, Headers.build {
                        append(HttpHeaders.ContentType, "image/png")
                        append(HttpHeaders.ContentDisposition, "filename=\"img2.png\"")
                    })
                }
            )

            if (response.status.isSuccess()) {
                result = response.body()
            } else {
                throw BadRequestException("inference server response failed: ${response.status} ${response.bodyAsText()}")
            }
        }

        return result
    }

    fun inferenceRecentImage(img: MultipartFile): ByteArray {
        val ktorClient = HttpClient(CIO) {
            install(ContentEncoding) {
                gzip() // Enable Gzip handling explicitly
            }
            install(HttpTimeout) {
                requestTimeoutMillis = 60_000 // 60초
                connectTimeoutMillis = 20_000
                socketTimeoutMillis = 60_000
            }
        }
        val imgBase64 = getLatestImageBase64List().first()
        val cleanBase64 = imgBase64.substringAfter(",") // "data:image/...;base64," 제거
        val imgBytes = Base64.getDecoder().decode(cleanBase64)
        val img2Bytes = img.bytes

//        return img1Bytes
        val result: ByteArray
        runBlocking {
            val response = ktorClient.submitFormWithBinaryData(
                url = "http://localhost:8086/predict/",
                formData = formData {
                    append("img1", imgBytes, Headers.build {
                        append(HttpHeaders.ContentType, "image/png")
                        append(HttpHeaders.ContentDisposition, "filename=\"img1.png\"")
                    })
                    append("img2", img2Bytes, Headers.build {
                        append(HttpHeaders.ContentType, "image/png")
                        append(HttpHeaders.ContentDisposition, "filename=\"img2.png\"")
                    })
                }
            )

            if (response.status.isSuccess()) {
                result = response.body()
            } else {
                throw BadRequestException("inference server response failed: ${response.status} ${response.bodyAsText()}")
            }
        }

        return result
    }

    @PostConstruct
    fun createFolder() {
        File(imagePath).mkdirs()

        val generatedUrls = File("generatedUrls.txt")
        if(!generatedUrls.exists()) generatedUrls.createNewFile()
    }

    fun generateFile(bufferedImage: BufferedImage): String {
        // 동기화된 파일 만들기
        // TODO 원자적 처리 추가 코딩 필요
        var file: File
        synchronized(this) {
            do {
                file = File("$imagePath/${UUID.randomUUID()}")
            } while (file.exists())
            file.createNewFile()
        }

        val res = ImageIO.write(bufferedImage, "png", file)
        logger.info("Generated url: ${file.path} $res ${bufferedImage.width} ${bufferedImage.height}")

        synchronized(this) {
            val generatedUrls = File("generatedUrls.txt")
            generatedUrls.appendText("${file.name}\n")
        }

        return file.name
    }

    fun getRecentUrls(): List<String> {
        val generatedUrls = File("generatedUrls.txt")
//        if(!generatedUrls.exists()) generatedUrls.createNewFile()

        return generatedUrls.readLines().takeLast(3)
    }

    fun getLatestImageBase64List(maxCount: Int = 1): List<String> {
        val folder = File(ftpFilePath)
        if (!folder.exists() || !folder.isDirectory) {
            throw IllegalArgumentException("Invalid folder path: $ftpFilePath")
        }

        val imageExtensions = listOf("jpg", "jpeg", "png", "gif", "bmp", "webp")

        return folder.listFiles { file ->
            file.isFile &&
                    imageExtensions.any { ext -> file.name.lowercase().endsWith(".$ext") &&
                            isValidImage(file)
                    }
        }?.sortedByDescending { it.lastModified() }
            ?.take(maxCount)
            ?.mapNotNull { file ->
                try {
                    encodeImageRotatedIfLandscape(file)
//                    if(file.name.lowercase().endsWith("jpg")) {
//                        convertJpgToPngBase64(file)
//                    } else {
//                        Base64.getEncoder().encodeToString(file.readBytes())
//                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                    null
                }
            }
            ?: emptyList()
    }

    fun convertJpgToPngBase64(jpgFile: File): String {
        // 1. 이미지 디코딩
        val image = ImageIO.read(jpgFile) // jpg 파일 → BufferedImage

        // 2. PNG로 인코딩하여 바이트 배열로 출력
        val outputStream = ByteArrayOutputStream()
        ImageIO.write(image, "jpg", outputStream)
        val pngBytes = outputStream.toByteArray()

        // 3. Base64 인코딩
        return Base64.getEncoder().encodeToString(pngBytes)
    }

    fun isValidImage(file: File): Boolean {
        return try {
            ImageIO.read(file)?.let { true } ?: false
        } catch (e: Exception) {
            false
        }
    }

    fun getImageFromFile(fileName: String): ByteArray {
        if(!isValidUUID(fileName)) throw BadRequestException("url is not valid")
        val file = File("$imagePath/$fileName")
        if(!file.exists()) throw BadRequestException("file does not exist")

        return file.readBytes()
    }
}

//fun byteArrayToMultipartFile(
//    bytes: ByteArray,
//    fieldName: String = "file",
//    fileName: String = "image.png",
//    contentType: String = "image/png"
//): MultipartFile {
//    return MockMultipartFile(
//        fieldName,        // name
//        fileName,         // original filename
//        contentType,      // content type
//        bytes             // file content
//    )
//}

fun encodeImageRotatedIfLandscape(file: File): String {
    // 1. 파일 → 이미지 디코딩
    val image: BufferedImage = ImageIO.read(file)

    // 2. 가로가 긴 경우 → 회전
    val processedImage = if (image.width > image.height) {
        rotateLeft90(image)
    } else {
        image
    }

    // 3. 이미지 → PNG 바이트로 인코딩
    val outputStream = ByteArrayOutputStream()
    ImageIO.write(processedImage, "png", outputStream)
    val pngBytes = outputStream.toByteArray()

    // 4. Base64 인코딩
    return Base64.getEncoder().encodeToString(pngBytes)
}

/**
 * 이미지를 왼쪽으로 90도 회전
 */
fun rotateLeft90(img: BufferedImage): BufferedImage {
    val w = img.width
    val h = img.height
    val rotated = BufferedImage(h, w, img.type)

    val g2d: Graphics2D = rotated.createGraphics()
    val transform = AffineTransform()

    // 왼쪽(반시계방향)으로 90도 회전: (0, 0) → (0, w)
    transform.translate(0.0, w.toDouble())
    transform.rotate(Math.toRadians(-90.0))

    g2d.transform = transform
    g2d.drawImage(img, 0, 0, null)
    g2d.dispose()

    return rotated
}