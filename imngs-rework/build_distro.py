from wiesel.wsl_distributions import Dockerfile

distro_from_dockerfile = Dockerfile(
    dockerfile_path="build/Dockerfile",
    docker_context_path="build",
    distribution_name="ngstoolkitdist-dev",
    install_location="."
)

distro = distro_from_dockerfile.build()
print(distro)
