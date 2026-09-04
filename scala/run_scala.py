import os
import subprocess
import glob

# 1. Locate java.exe in Coursier cache
coursier_dir = os.path.expanduser(r"~\AppData\Local\Coursier")
javas = glob.glob(os.path.join(coursier_dir, "**", "java.exe"), recursive=True)
if not javas:
    raise RuntimeError("java.exe not found in Coursier cache")

java_bin = javas[0]
print(f"Using JVM: {java_bin}")

# 2. Get scala3 classpath via coursier
cs_bin = os.path.expanduser(r"~\AppData\Local\Coursier\data\bin\cs.bat")
res = subprocess.run([cs_bin, "fetch", "org.scala-lang:scala3-library_3:3.9.0"], capture_output=True, text=True, check=True)
jars = [line.strip() for line in res.stdout.splitlines() if line.strip().endswith(".jar")]
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
cp = os.pathsep.join([out_dir] + jars)

# 3. Run kuwala.Main
print("Running kuwala.Main...")
result = subprocess.run([java_bin, "-cp", cp, "kuwala.Main"], text=True)
if result.returncode != 0:
    print(f"Failed with exit code: {result.returncode}")
    exit(result.returncode)
