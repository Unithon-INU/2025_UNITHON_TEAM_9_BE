package kr.goldenmine.chakbootbackend

//import io.swagger.v3.oas.annotations.Hidden
import jakarta.annotation.PostConstruct
import org.apache.coyote.BadRequestException
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.security.authentication.BadCredentialsException
import org.springframework.web.bind.annotation.*

@RestControllerAdvice
//@Hidden
class ExceptionAdvice {
    private val logger: Logger = LoggerFactory.getLogger(ExceptionAdvice::class.java)

    @PostConstruct
    fun init() {
        logger.info("ExceptionAdvice has been initialized.")
    }

    @ExceptionHandler(BadCredentialsException::class)
    @ResponseStatus(value = HttpStatus.FORBIDDEN)
    @ResponseBody
    fun handleBadCredentialsException(e: BadCredentialsException): Map<String, String> {
        val retMessages = HashMap<String, String>()
        retMessages["message"] = e.message ?: "null"
        return retMessages
    }

    @ExceptionHandler(BadRequestException::class)
    @ResponseStatus(value = HttpStatus.BAD_REQUEST)
    @ResponseBody
    fun handleBadRequestException(e: BadRequestException): Map<String, String> {
        val retMessages = HashMap<String, String>()
        retMessages["message"] = e.message.toString()
        return retMessages
    }

//    @ExceptionHandler(ConflictException::class)
//    @ResponseStatus(value = HttpStatus.CONFLICT)
//    @ResponseBody
//    fun handleConflictException(e: ConflictException): Map<String, String> {
//        val retMessages = HashMap<String, String>()
//        retMessages["message"] = e.message
//        return retMessages
//    }
}