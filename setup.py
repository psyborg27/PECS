from setuptools import find_packages, setup

setup(
    name="pecs_pro",
    version="1.0.0-alpha1",
    description="PECS-PRO workspace continuity cache and daemon",
    packages=find_packages(where="."),
    py_modules=[
        "append_ai_chat_history",
        "install_workspace_integration",
        "run_pecs_daemon",
        "run_pecs_lite_v2_daemon",
        "run_pecs_pro",
        "workspace_assets_manager",
        "workspace_bridge_cli",
    ],
    install_requires=["watchdog>=3.0.0,<4.0.0"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "pecs-pro=workspace_bridge_cli:main",
            "pecs=workspace_bridge_cli:main",
            "pecs-pro-daemon=run_pecs_daemon:main",
            "pecs-pro-install-workspace=install_workspace_integration:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
