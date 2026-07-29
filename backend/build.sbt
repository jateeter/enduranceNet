name := "endurancenet-backend"
version := "1.0.0"
scalaVersion := "3.3.3"

lazy val root = (project in file("."))
  .enablePlugins(PlayScala)
  .settings(
    libraryDependencies ++= Seq(
      guice,
      "org.scalatestplus.play" %% "scalatestplus-play" % "7.0.1" % Test,
      "com.h2database" % "h2" % "2.2.224" % Test,
      "org.playframework" %% "play-slick" % "6.1.0",
      "org.playframework" %% "play-slick-evolutions" % "6.1.0",
      "com.h2database" % "h2" % "2.2.224"
    ),
    scalacOptions ++= Seq(
      "-deprecation",
      "-feature",
      "-unchecked"
    )
  )
