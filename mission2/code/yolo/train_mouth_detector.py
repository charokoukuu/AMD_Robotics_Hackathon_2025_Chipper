"""
口の開閉検出モデルのトレーニングスクリプト

使い方:
1. データセット収集: python train_mouth_detector.py --collect
2. アノテーション: RoboflowやLabelImgでラベル付け
3. トレーニング: python train_mouth_detector.py --train
"""

import cv2
import os
from pathlib import Path
import argparse
from ultralytics import YOLO
import yaml


def collect_data(output_dir="yolo/mouth_dataset", num_samples=100, camera_index=5):
    """カメラから口の画像を収集"""
    output_dir = Path(output_dir)
    open_dir = output_dir / "images" / "open"
    close_dir = output_dir / "images" / "close"
    chip_dir = output_dir / "images" / "chip"

    open_dir.mkdir(parents=True, exist_ok=True)
    close_dir.mkdir(parents=True, exist_ok=True)
    chip_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(5)

    print("データ収集モード")
    print("'o' キー: 口を開けた状態で保存")
    print("'c' キー: 口を閉じた状態で保存")
    print("'p' キー: ポテトチップスを咥えた状態で保存")
    print("'q' キー: 終了")

    open_count = 0
    close_count = 0
    chip_count = 0

    while (
        open_count < num_samples
        or close_count < num_samples
        or chip_count < num_samples
    ):
        ret, frame = cap.read()
        if not ret:
            break

        # 状態を表示
        status = f"Open: {open_count}/{num_samples} | Close: {close_count}/{num_samples} | Chip: {chip_count}/{num_samples}"
        cv2.putText(
            frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

        cv2.imshow("Data Collection", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("o") and open_count < num_samples:
            # 口を開けた画像を保存
            filename = open_dir / f"open_{open_count:04d}.jpg"
            cv2.imwrite(str(filename), frame)
            print(f"保存: {filename}")
            open_count += 1

        elif key == ord("c") and close_count < num_samples:
            # 口を閉じた画像を保存
            filename = close_dir / f"close_{close_count:04d}.jpg"
            cv2.imwrite(str(filename), frame)
            print(f"保存: {filename}")
            close_count += 1

        elif key == ord("p") and chip_count < num_samples:
            # ポテトチップスを咥えた画像を保存
            filename = chip_dir / f"chip_{chip_count:04d}.jpg"
            cv2.imwrite(str(filename), frame)
            print(f"保存: {filename}")
            chip_count += 1

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"\nデータ収集完了!")
    print(f"口を開けた画像: {open_count}枚")
    print(f"口を閉じた画像: {close_count}枚")
    print(f"ポテトチップスを咥えた画像: {chip_count}枚")
    print(f"\n次のステップ:")
    print("python train_mouth_detector.py --train-cls でモデルをトレーニング")


def create_dataset_yaml(dataset_path="mouth_dataset"):
    """データセット設定ファイルを作成"""
    dataset_path = Path(dataset_path)

    config = {
        "path": str(dataset_path.absolute()),
        "train": "images/train",
        "val": "images/val",
        "names": {0: "mouth_open", 1: "mouth_close"},
        "nc": 2,  # クラス数
    }

    yaml_path = dataset_path / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"データセット設定ファイル作成: {yaml_path}")
    return yaml_path


def train_model(dataset_yaml="mouth_dataset/data.yaml", epochs=100, img_size=640):
    """YOLOv8モデルをトレーニング"""
    print("モデルのトレーニングを開始...")

    # YOLOv8nanoモデルをベースにする（軽量・高速）
    model = YOLO("yolov8n.pt")

    # トレーニング開始
    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=16,
        patience=20,  # Early stopping
        save=True,
        project="mouth_detection",
        name="mouth_model",
        verbose=True,
    )

    print("\nトレーニング完了!")
    print(f"モデル保存先: mouth_detection/mouth_model/weights/best.pt")

    return results


def train_classification_model(data_dir="mouth_dataset/images", epochs=50):
    """分類モデルとしてトレーニング（より簡単）"""
    print("分類モデルのトレーニングを開始...")

    # YOLOv8 分類モデル
    model = YOLO("yolov8n-cls.pt")

    results = model.train(
        data=data_dir,
        epochs=epochs,
        imgsz=224,
        batch=32,
        project="mouth_classification",
        name="mouth_cls_model",
        verbose=True,
    )

    print("\nトレーニング完了!")
    print(f"モデル保存先: mouth_classification/mouth_cls_model/weights/best.pt")

    return results


def main():
    parser = argparse.ArgumentParser(description="口の開閉検出モデルのトレーニング")
    parser.add_argument("--collect", action="store_true", help="データ収集モード")
    parser.add_argument(
        "--train-cls", action="store_true", help="分類モデルをトレーニング"
    )
    parser.add_argument(
        "--train-detect", action="store_true", help="検出モデルをトレーニング"
    )
    parser.add_argument(
        "--dataset", type=str, default="mouth_dataset", help="データセットのパス"
    )
    parser.add_argument("--epochs", type=int, default=50, help="エポック数")
    parser.add_argument(
        "--samples", type=int, default=100, help="収集するサンプル数（各クラス）"
    )
    parser.add_argument(
        "--camera", type=int, default=4, help="使用するカメラインデックス"
    )

    args = parser.parse_args()

    if args.collect:
        # データ収集
        collect_data(args.dataset, args.samples, args.camera)

    elif args.train_cls:
        # 分類モデルのトレーニング（推奨・簡単）
        data_dir = Path(args.dataset) / "images"
        if not data_dir.exists():
            print(f"エラー: データセットが見つかりません: {data_dir}")
            return
        train_classification_model(str(data_dir), args.epochs)

    elif args.train_detect:
        # 検出モデルのトレーニング（上級者向け）
        yaml_path = create_dataset_yaml(args.dataset)
        train_model(str(yaml_path), args.epochs)

    else:
        print("使い方:")
        print("  データ収集: python train_mouth_detector.py --collect")
        print("  分類モデル学習: python train_mouth_detector.py --train-cls")
        print("  検出モデル学習: python train_mouth_detector.py --train-detect")


if __name__ == "__main__":
    main()
