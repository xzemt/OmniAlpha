#!/usr/bin/env python3
"""
OmniAlpha 项目统一启动入口
支持同时启动前后端服务

Usage:
    python run.py --mode all          # 启动前后端
    python run.py --mode backend      # 仅启动后端
    python run.py --mode frontend     # 仅启动前端
    python run.py --mode web          # 启动 Streamlit Web UI
"""

import argparse
import subprocess
import os
import sys
import signal
import time
from pathlib import Path
from typing import Optional, List
import atexit


class ProjectRunner:
    """项目多进程启动管理器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.processes: List[subprocess.Popen] = []
        self.os_type = sys.platform

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理所有进程"""
        self.cleanup()

    def cleanup(self):
        """清理所有运行中的进程"""
        for process in self.processes:
            if process.poll() is None:  # 进程仍在运行
                try:
                    if self.os_type == "win32":
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=5)
                except (ProcessLookupError, subprocess.TimeoutExpired):
                    process.kill()

        self.processes.clear()
        print("\n✓ 所有进程已清理")

    def run_backend(self) -> Optional[subprocess.Popen]:
        """启动 FastAPI 后端服务"""
        try:
            print("\n🚀 启动后端服务 (FastAPI)...")
            print("   端口: http://localhost:8000")
            print("   文档: http://localhost:8000/docs")

            # 使用绝对路径和完整的模块导入
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.app.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                    "--reload",
                ],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if self.os_type != "win32" else None,
                text=True,
            )

            self.processes.append(process)
            time.sleep(2)  # 给后端启动时间
            print("✓ 后端服务启动成功")
            return process

        except Exception as e:
            print(f"✗ 后端启动失败: {e}")
            return None

    def run_frontend(self) -> Optional[subprocess.Popen]:
        """启动 React 前端开发服务"""
        frontend_dir = self.project_root / "frontend"

        if not frontend_dir.exists():
            print("✗ 前端目录不存在")
            return None

        try:
            print("\n🎨 启动前端服务 (React + Vite)...")
            print("   端口: http://localhost:5173")

            # 检查 node_modules
            if not (frontend_dir / "node_modules").exists():
                print("   📦 首次运行，正在安装依赖...")
                subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    check=True,
                    capture_output=True,
                )

            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if self.os_type != "win32" else None,
                text=True,
            )

            self.processes.append(process)
            time.sleep(3)  # 给前端启动时间
            print("✓ 前端服务启动成功")
            return process

        except FileNotFoundError:
            print("✗ npm 未安装，请先安装 Node.js")
            return None
        except Exception as e:
            print(f"✗ 前端启动失败: {e}")
            return None

    def run_streamlit(self) -> Optional[subprocess.Popen]:
        """启动 Streamlit Web UI"""
        try:
            print("\n📊 启动 Streamlit Web UI...")
            print("   端口: http://localhost:8501")

            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "web_ui.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if self.os_type != "win32" else None,
                text=True,
            )

            self.processes.append(process)
            time.sleep(2)
            print("✓ Streamlit Web UI 启动成功")
            return process

        except Exception as e:
            print(f"✗ Streamlit 启动失败: {e}")
            return None

    def run_all(self):
        """同时启动后端和前端"""
        print("\n" + "=" * 60)
        print("   OmniAlpha 项目启动器 (前后端一体化)")
        print("=" * 60)

        backend_process = self.run_backend()
        frontend_process = self.run_frontend()

        if not backend_process and not frontend_process:
            print("\n✗ 启动失败，请检查依赖和配置")
            return False

        print("\n" + "=" * 60)
        print("✓ 服务启动完成！")
        print("=" * 60)
        print("\n📍 访问地址:")
        print("   • 前端工作台: http://localhost:5173")
        print("   • 后端 API: http://localhost:8000")
        print("   • API 文档: http://localhost:8000/docs")
        print("\n⌨️  按 Ctrl+C 停止所有服务")
        print("=" * 60 + "\n")

        try:
            # 保持进程运行
            while True:
                # 检查进程状态
                for process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  进程已退出 (PID: {process.pid})")

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⚠️  收到停止信号，正在关闭所有服务...")
            self.cleanup()

    def run_mode(self, mode: str):
        """根据模式运行"""
        try:
            if mode == "all":
                self.run_all()
            elif mode == "backend":
                self.run_backend()
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n⚠️  关闭后端服务...")
                    self.cleanup()
            elif mode == "frontend":
                self.run_frontend()
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n⚠️  关闭前端服务...")
                    self.cleanup()
            elif mode == "web":
                self.run_streamlit()
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n⚠️  关闭 Streamlit...")
                    self.cleanup()
            else:
                print(f"✗ 未知的模式: {mode}")
                sys.exit(1)
        except Exception as e:
            print(f"✗ 运行错误: {e}")
            self.cleanup()
            sys.exit(1)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="OmniAlpha 项目启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run.py --mode all          # 启动前后端
  python run.py --mode backend      # 仅启动后端
  python run.py --mode frontend     # 仅启动前端
  python run.py --mode web          # 启动 Streamlit Web UI
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["all", "backend", "frontend", "web"],
        default="all",
        help="启动模式 (默认: all)",
    )

    args = parser.parse_args()
    project_root = Path(__file__).parent.absolute()

    with ProjectRunner(project_root) as runner:
        runner.run_mode(args.mode)


if __name__ == "__main__":
    main()
