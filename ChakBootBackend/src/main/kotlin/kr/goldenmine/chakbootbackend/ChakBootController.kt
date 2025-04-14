package kr.goldenmine.chakbootbackend

import kr.goldenmine.chakbootbackend.dto.ResponsePrediction
import kr.goldenmine.chakbootbackend.util.byteArrayToBufferedImage
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestPart
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.multipart.MultipartFile
import java.util.*

@RestController
@RequestMapping("/ai")
class ChakBootController(
    private val chakbootService: ChakbootService,
) {
    @PostMapping("/predict", consumes = [MediaType.MULTIPART_FORM_DATA_VALUE])
    fun handlePrediction(
        @RequestPart("img1") img1: MultipartFile,
        @RequestPart("img2") img2: MultipartFile
    ): ResponseEntity<ResponsePrediction> {
        val result = chakbootService.inferenceImage(img1, img2)
//        val base64Image = Base64Utils.encodeToString(result)
        val base64Image = Base64.getEncoder().encodeToString(result)
        val url = chakbootService.generateUrl(byteArrayToBufferedImage(result))

        return ResponseEntity
            .ok()
            .contentType(MediaType.APPLICATION_JSON)
            .body(ResponsePrediction(
                imageBase64 = base64Image,
                url = url,
            ))
    }
}