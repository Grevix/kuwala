name := "kuwala-scala"
organization := "org.kuwala"
version := "0.2.0"
scalaVersion := "2.13.14"

crossScalaVersions := Seq("2.13.14", "3.3.3")

libraryDependencies ++= Seq(
  "org.apache.arrow" % "arrow-vector" % "16.1.0",
  "org.apache.arrow" % "arrow-memory-netty" % "16.1.0",
  "org.scalatest" %% "scalatest" % "3.2.18" % Test
)

scalacOptions ++= Seq(
  "-encoding", "utf8",
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Xfatal-warnings",
  "-opt:l:inline"
)
