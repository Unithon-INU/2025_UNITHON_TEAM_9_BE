package kr.goldenmine.chakbootbackend

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.web.SecurityFilterChain

@Configuration
class SecurityConfig{
    @Bean
    fun filterChain(http: HttpSecurity): SecurityFilterChain {
        // 어차피 뭐 로그인할 껀덕지도 없으니 그냥 오픈
        http
            .csrf { it.disable() }
            .authorizeHttpRequests {
                it.requestMatchers("/**").permitAll()
//                it.anyRequest().authenticated()
            }

        return http.build()
    }
}