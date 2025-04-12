package kr.goldenmine.chakbootbackend

import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface ImageQRCodeRepository: JpaRepository<ImageQRCode, Long> {
    fun existsImageQRCodeByFileName(fileName: String): Boolean
}