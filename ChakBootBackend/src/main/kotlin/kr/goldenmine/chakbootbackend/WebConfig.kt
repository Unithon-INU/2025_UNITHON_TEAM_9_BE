package kr.goldenmine.chakbootbackend

import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Configuration
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer
import java.nio.file.Paths

@Configuration
class WebConfig(
    @Value("\${app.image.upload-dir}") private val uploadDir: String,
    @Value("\${app.image.serve-path}") private val servePath: String
) : WebMvcConfigurer {

    private val logger = LoggerFactory.getLogger(WebConfig::class.java)

    override fun addResourceHandlers(registry: ResourceHandlerRegistry) {
        val resourceLocation = Paths.get(uploadDir).toUri().toString()
        val pathPattern = "$servePath/**" // 예: /images/**

        logger.info("Configuring static resource handler:")
        logger.info("  Path Pattern: {}", pathPattern)
        logger.info("  Resource Location: {}", resourceLocation)

        registry.addResourceHandler(pathPattern)
            .addResourceLocations(resourceLocation)

        // 캐싱 비활성화 (개발 중 또는 필요에 따라 설정)
        // .setCachePeriod(0)
    }
}