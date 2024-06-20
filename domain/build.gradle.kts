plugins {
    id("java-library")
    alias(libs.plugins.jetbrainsKotlinJvm)
    id("kotlin-kapt")
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

dependencies {
    implementation ("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}