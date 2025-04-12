package kr.goldenmine.chakbootbackend

import jakarta.persistence.*

@Entity
@Table(name = "image_qrcode")
class ImageQRCode(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0L,

    @Column(unique = true)
    val fileName: String,
) {
}