package kr.goldenmine.chakbootbackend

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
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
import java.awt.image.BufferedImage
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

//        return img1Bytes
        val result: ByteArray?
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
                result = null
                logger.warn("django response failed: ${response.status} ${response.bodyAsText()}")
            }
        }

        return result ?: throw BadRequestException("에러 발생")
    }

    @PostConstruct
    fun createFolder() {
        File(imagePath).mkdirs()
    }

    fun generateFile(bufferedImage: BufferedImage): String {
        // 동기화된 파일 만들기
        var file: File
        synchronized(this) {
            do {
                file = File("$imagePath/${UUID.randomUUID()}")
            } while (file.exists())
            file.createNewFile()
        }

        val res = ImageIO.write(bufferedImage, "png", file)
        logger.info("Generated url: ${file.path} $res ${bufferedImage.width} ${bufferedImage.height}")

        return file.name
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
