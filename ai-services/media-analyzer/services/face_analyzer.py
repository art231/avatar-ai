import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import insightface
from insightface.app import FaceAnalysis
import logging
from loguru import logger
import albumentations as A
from albumentations.pytorch import ToTensorV2
import torch
from PIL import Image
import io

class FaceAnalyzer:
    """Face analyzer using InsightFace for detection, alignment, and quality assessment."""
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.face_app = None
        self.logger = logger
        
        # Face quality thresholds
        self.min_face_quality = 0.7
        self.min_face_size = 100  # pixels
        self.max_face_size = 1000  # pixels
        
        # Initialize InsightFace
        self._init_insightface()
        
        # Define augmentation for face alignment
        self.alignment_transform = A.Compose([
            A.Resize(512, 512),
            A.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            ToTensorV2(),
        ])
    
    def _init_insightface(self):
        """Initialize InsightFace model."""
        try:
            self.logger.info("Initializing InsightFace model...")
            
            # Create face analysis app
            self.face_app = FaceAnalysis(
                name='buffalo_l',  # Use buffalo_l model for best accuracy
                providers=['CUDAExecutionProvider'] if self.device == 'cuda' else ['CPUExecutionProvider']
            )
            
            # Prepare the model
            self.face_app.prepare(ctx_id=0 if self.device == 'cuda' else -1, det_size=(640, 640))
            
            self.logger.info("InsightFace model initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize InsightFace: {e}")
            raise
    
    def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Analyze image for face detection and quality assessment.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load image
            self.logger.info(f"Analyzing image: {image_path}")
            img = cv2.imread(str(image_path))
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width = img_rgb.shape[:2]
            
            # Detect faces
            faces = self.face_app.get(img_rgb)
            
            if not faces:
                raise ValueError("No faces detected in the image")
            
            self.logger.info(f"Detected {len(faces)} face(s)")
            
            # Process each face
            face_results = []
            for i, face in enumerate(faces):
                face_result = self._process_face(face, i, img_rgb)
                face_results.append(face_result)
            
            # Get best face (highest quality)
            best_face = max(face_results, key=lambda f: f['quality_score'])
            
            # Overall image quality assessment
            quality_assessment = self._assess_image_quality(img_rgb, face_results)
            
            return {
                "image_info": {
                    "resolution": [width, height],
                    "channels": img_rgb.shape[2] if len(img_rgb.shape) > 2 else 1,
                    "aspect_ratio": width / height
                },
                "faces": face_results,
                "best_face": best_face,
                "quality_assessment": quality_assessment,
                "validation_passed": best_face['quality_score'] >= self.min_face_quality
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            raise
    
    def _process_face(self, face: Any, face_id: int, image: np.ndarray) -> Dict[str, Any]:
        """Process individual face detection result."""
        # Extract bounding box
        bbox = face.bbox.astype(int)
        x1, y1, x2, y2 = bbox
        
        # Calculate face size
        face_width = x2 - x1
        face_height = y2 - y1
        face_size = max(face_width, face_height)
        
        # Calculate quality score based on multiple factors
        quality_score = self._calculate_face_quality(face, image)
        
        # Extract landmarks
        landmarks = face.kps.tolist() if hasattr(face, 'kps') else []
        
        # Get face attributes
        age = int(face.age) if hasattr(face, 'age') else 30
        gender = "female" if hasattr(face, 'gender') and face.gender == 0 else "male"
        
        # Calculate detection confidence
        det_score = float(face.det_score) if hasattr(face, 'det_score') else 0.95
        
        # Check if face is frontal
        is_frontal = self._is_frontal_face(landmarks) if landmarks else True
        
        # Check for occlusion
        is_occluded = self._check_occlusion(bbox, image)
        
        return {
            "face_id": face_id,
            "bounding_box": bbox.tolist(),
            "landmarks": landmarks,
            "quality_score": float(quality_score),
            "detection_confidence": float(det_score),
            "age": age,
            "gender": gender,
            "face_size": face_size,
            "is_frontal": is_frontal,
            "is_occluded": is_occluded,
            "emotion": "neutral",  # Could be extended with emotion detection
            "aligned_face_path": None
        }
    
    def _calculate_face_quality(self, face: Any, image: np.ndarray) -> float:
        """Calculate comprehensive face quality score."""
        quality_factors = []
        
        # 1. Detection confidence
        if hasattr(face, 'det_score'):
            quality_factors.append(float(face.det_score))
        
        # 2. Face size factor (normalized)
        bbox = face.bbox.astype(int)
        face_size = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
        size_factor = min(1.0, face_size / 300.0)  # Normalize to 300px
        quality_factors.append(size_factor)
        
        # 3. Face clarity (using landmark confidence)
        if hasattr(face, 'landmark_3d_68'):
            # Check if landmarks are detected well
            landmark_quality = 0.9  # Placeholder
            quality_factors.append(landmark_quality)
        
        # 4. Brightness and contrast of face region
        face_region = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
        if face_region.size > 0:
            brightness = np.mean(face_region) / 255.0
            # Ideal brightness is around 0.5
            brightness_factor = 1.0 - abs(brightness - 0.5)
            quality_factors.append(brightness_factor)
            
            # Contrast
            contrast = np.std(face_region) / 255.0 if face_region.size > 1 else 0
            contrast_factor = min(1.0, contrast * 2)  # Normalize
            quality_factors.append(contrast_factor)
        
        # Average all factors
        if quality_factors:
            quality_score = np.mean(quality_factors)
        else:
            quality_score = 0.7  # Default
        
        return float(quality_score)
    
    def _is_frontal_face(self, landmarks: List[List[float]]) -> bool:
        """Check if face is frontal based on landmarks."""
        if len(landmarks) < 5:
            return True
        
        # Simple check: compare eye positions
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        nose = landmarks[2]
        
        # Calculate eye alignment
        eye_distance = abs(left_eye[0] - right_eye[0])
        eye_height_diff = abs(left_eye[1] - right_eye[1])
        
        # If eyes are at similar height and properly spaced, face is likely frontal
        return eye_height_diff < eye_distance * 0.1
    
    def _check_occlusion(self, bbox: np.ndarray, image: np.ndarray) -> bool:
        """Check if face is occluded (simple edge detection)."""
        x1, y1, x2, y2 = bbox
        face_region = image[y1:y2, x1:x2]
        
        if face_region.size == 0:
            return True
        
        # Convert to grayscale
        gray = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY) if len(face_region.shape) == 3 else face_region
        
        # Calculate edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # High edge density might indicate occlusion or texture
        # This is a simple heuristic
        return edge_density > 0.3
    
    def _assess_image_quality(self, image: np.ndarray, faces: List[Dict]) -> Dict[str, Any]:
        """Assess overall image quality."""
        # Convert to grayscale for quality metrics
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Calculate blurriness (Laplacian variance)
        blurriness = cv2.Laplacian(gray, cv2.CV_64F).var()
        blurriness_score = min(1.0, blurriness / 100.0)  # Normalize
        
        # Calculate brightness
        brightness = np.mean(gray) / 255.0
        brightness_score = 1.0 - abs(brightness - 0.5)  # Ideal is 0.5
        
        # Calculate contrast
        contrast = np.std(gray) / 255.0 if gray.size > 1 else 0
        contrast_score = min(1.0, contrast * 2)  # Normalize
        
        # Calculate noise (using median absolute deviation)
        if gray.size > 1:
            median = np.median(gray)
            mad = np.median(np.abs(gray - median))
            noise_level = mad / 255.0
            noise_score = max(0.0, 1.0 - noise_level * 5)  # Lower noise is better
        else:
            noise_score = 0.8
        
        # Face-specific quality
        face_quality_scores = [face['quality_score'] for face in faces]
        avg_face_quality = np.mean(face_quality_scores) if face_quality_scores else 0
        
        return {
            "image_quality": {
                "blurriness": float(blurriness_score),
                "brightness": float(brightness_score),
                "contrast": float(contrast_score),
                "noise": float(noise_score),
                "overall": float(np.mean([blurriness_score, brightness_score, contrast_score, noise_score]))
            },
            "face_quality": [
                {
                    "face_id": face['face_id'],
                    "quality_score": face['quality_score'],
                    "detection_confidence": face['detection_confidence'],
                    "is_frontal": face['is_frontal'],
                    "is_occluded": face['is_occluded']
                }
                for face in faces
            ],
            "average_face_quality": float(avg_face_quality)
        }
    
    def align_and_save_faces(self, image_path: Path, faces: List[Dict], output_dir: Path) -> List[Dict]:
        """
        Align faces and save them as separate images.
        
        Args:
            image_path: Path to original image
            faces: List of face dictionaries from analyze_image
            output_dir: Directory to save aligned faces
            
        Returns:
            Updated faces list with aligned_face_path
        """
        try:
            # Load image
            img = cv2.imread(str(image_path))
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            updated_faces = []
            for face in faces:
                bbox = face['bounding_box']
                x1, y1, x2, y2 = bbox
                
                # Extract face region
                face_region = img_rgb[y1:y2, x1:x2]
                if face_region.size == 0:
                    continue
                
                # Resize to 512x512
                face_resized = cv2.resize(face_region, (512, 512))
                
                # Save aligned face
                aligned_filename = f"face_{face['face_id']:03d}.jpg"
                aligned_path = output_dir / aligned_filename
                
                # Convert back to BGR for OpenCV save
                face_bgr = cv2.cvtColor(face_resized, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(aligned_path), face_bgr)
                
                # Update face with aligned path
                face['aligned_face_path'] = str(aligned_path)
                updated_faces.append(face)
            
            return updated_faces
            
        except Exception as e:
            self.logger.error(f"Error aligning faces: {e}")
            return faces
    
    def validate_image(self, image_path: Path) -> Tuple[bool, str]:
        """
        Validate image for avatar generation.
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Check file exists
            if not image_path.exists():
                return False, f"Image file not found: {image_path}"
            
            # Analyze image
            analysis = self.analyze_image(image_path)
            
            # Check if faces detected
            if not analysis['faces']:
                return False, "No faces detected in the image"
            
            # Check face quality
            best_face = analysis['best_face']
            if best_face['quality_score'] < self.min_face_quality:
                return False, f"Face quality too low: {best_face['quality_score']:.2f}. Minimum: {self.min_face_quality}"
            
            # Check face size
            if best_face['face_size'] < self.min_face_size:
                return False, f"Face too small: {best_face['face_size']}px. Minimum: {self.min_face_size}px"
            
            # Check if frontal
            if not best_face['is_frontal']:
                return False, "Face is not frontal. Please use a frontal face image."
            
            # Check occlusion
            if best_face['is_occluded']:
                return False, "Face appears to be occluded. Please use a clear image."
            
            return True, "Image is valid for avatar generation"
            
        except Exception as e:
            return False, f"Image validation failed: {str(e)}"
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of face analyzer."""
        return {
            "model_loaded": self.face_app is not None,
            "device": self.device,
            "min_face_quality": self.min_face_quality,
            "min_face_size": self.min_face_size
        }