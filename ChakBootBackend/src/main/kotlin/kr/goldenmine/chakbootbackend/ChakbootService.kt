package kr.goldenmine.chakbootbackend

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.compression.*
import io.ktor.client.request.forms.*
import io.ktor.client.statement.*
import io.ktor.http.*
import kotlinx.coroutines.runBlocking
import org.apache.coyote.BadRequestException
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import java.awt.image.BufferedImage
import java.io.ByteArrayInputStream
import java.io.File
import java.util.*
import javax.imageio.ImageIO

@Service
class ChakbootService(
    @Value("\${app.image_path}") private val imagePath: String
) {
    private val logger: Logger = LoggerFactory.getLogger(ChakbootService::class.java)

    fun inferenceImage(img1: MultipartFile, img2: MultipartFile): ByteArray {
        val ktorClient = HttpClient(CIO) {
            install(ContentEncoding) {
                gzip() // Enable Gzip handling explicitly
            }
        }
        val img1Bytes = img1.bytes
        val img2Bytes = img2.bytes

        val result: ByteArray?
        runBlocking {
            val response = ktorClient.submitFormWithBinaryData(
                url = "http://localhost:8085/predict/",
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
                result = null
                logger.warn("django response failed: ${response.status} ${response.bodyAsText()}")
            }
        }

        return result ?: throw BadRequestException("에러 발생")
//        return byteArrayToMultipartFile(result ?: throw BadRequestException("에러 발생"))
    }

    fun generateUrl(bufferedImage: BufferedImage): String {
        var file: File

        // 새로운 생성
        synchronized(this) {
            do {
                file = File("$imagePath/${UUID.randomUUID()}")
            } while (file.exists())
            file.createNewFile()
        }

        ImageIO.write(bufferedImage, "jpg", file)

        return file.name
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

fun byteArrayToBufferedImage(bytes: ByteArray): BufferedImage {
    val inputStream = ByteArrayInputStream(bytes)
    return ImageIO.read(inputStream) ?: throw IllegalArgumentException("Invalid image byte array")
}