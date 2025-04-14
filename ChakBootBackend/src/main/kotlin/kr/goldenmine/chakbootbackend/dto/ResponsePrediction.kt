package kr.goldenmine.chakbootbackend.dto

class ResponsePrediction(
    val imageBase64: String,
    val url: String,
) {

    override fun toString(): String {
        val maxLen = imageBase64.length.coerceAtMost(20)
        return "ResponsePrediction(imageBase64=${imageBase64.substring(0, maxLen)}..., url=$url)"
    }
}