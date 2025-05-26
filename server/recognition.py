import os
from typing import Dict, List, Optional
import numpy as np
import cv2
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import faiss
import joblib
from fastapi import HTTPException
from pydantic_settings import BaseSettings
from typing import ClassVar


class Settings(BaseSettings):
    students_dir: str = "students_images"
    dist_threshold: float = 0.8
    embedding_size: int = 512
    index_path: str = "models/face_index.faiss"
    mapping_path: str = "models/label_map.pkl"
    device: ClassVar[torch.device] = (
        torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    )


settings = Settings()


class FaceRecognizer:
    def __init__(
            self,
            students_dir: str,
            dist_threshold: float,
            device: torch.device,
            index_path: str,
            mapping_path: str,
    ):
        self.students_dir = students_dir
        self.dist_threshold = dist_threshold
        self.device = device
        self.index_path = index_path
        self.mapping_path = mapping_path

        # MTCNN on CPU to avoid MPS pool issues
        self.mtcnn_cpu = MTCNN(image_size=160, margin=0, device=torch.device("cpu"))
        # ResNet on chosen device
        self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)

        self.index: Optional[faiss.IndexFlatL2] = None
        self.label_map: Dict[int, str] = {}
        self.embedding_labels: List[int] = []  # index -> class label
        self._load_index()

    def _load_index(self) -> None:
        labels_file = self.mapping_path.replace('.pkl', '_labels.npy')
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path) and os.path.exists(labels_file):
            self.index = faiss.read_index(self.index_path)
            self.label_map = joblib.load(self.mapping_path)
            self.embedding_labels = np.load(labels_file).tolist()
        else:
            self.build_embedding_db()

    def build_embedding_db(self, target_class: Optional[str] = None) -> None:
        embeddings: List[np.ndarray] = []
        labels: List[int] = []
        self.label_map.clear()

        dirs = [target_class] if target_class else sorted(os.listdir(self.students_dir))
        for label, name in enumerate(dirs):
            path = os.path.join(self.students_dir, name)
            if not os.path.isdir(path):
                continue
            self.label_map[label] = name
            for file in sorted(os.listdir(path)):
                if not file.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img_path = os.path.join(path, file)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                face = self.mtcnn_cpu(rgb)
                if face is None:
                    continue
                tensor = face.unsqueeze(0).to(self.device)
                emb = self.resnet(tensor).detach().cpu().numpy()[0]
                embeddings.append(emb)
                labels.append(label)

        if not embeddings:
            raise RuntimeError("No embeddings found.")

        data = np.vstack(embeddings).astype('float32')
        lbls_arr = np.array(labels, dtype='int64')

        self.index = faiss.IndexFlatL2(settings.embedding_size)
        self.index.add(data)

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        joblib.dump(self.label_map, self.mapping_path)

        labels_file = self.mapping_path.replace('.pkl', '_labels.npy')
        os.makedirs(os.path.dirname(labels_file), exist_ok=True)
        np.save(labels_file, lbls_arr)
        self.embedding_labels = labels

    def _get_embedding(self, image: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face = self.mtcnn_cpu(rgb)
        if face is None:
            return np.empty((0, settings.embedding_size), dtype='float32')
        tensor = face.unsqueeze(0).to(self.device)
        emb = self.resnet(tensor).detach().cpu().numpy()
        return emb.astype('float32')

    def predict(self, image: np.ndarray, top_k: int = 1) -> List[Dict[str, float]]:
        if self.index is None:
            raise HTTPException(status_code=503, detail="Index not initialized")
        emb = self._get_embedding(image)
        if emb.size == 0:
            return []
        dists, ids = self.index.search(emb, top_k)
        results: List[Dict[str, float]] = []
        for dist, idx in zip(dists[0], ids[0]):
            label = self.embedding_labels[idx] if idx < len(self.embedding_labels) else None
            name = self.label_map.get(label, "Unknown")
            matched = float(dist) < settings.dist_threshold
            results.append({
                "name": name if matched else "Unknown",
                "distance": float(dist),
                "matched": bool(matched),
            })
        return results


# Singleton for FastAPI
face_recognizer = FaceRecognizer(
    students_dir=settings.students_dir,
    dist_threshold=settings.dist_threshold,
    device=settings.device,
    index_path=settings.index_path,
    mapping_path=settings.mapping_path,
)