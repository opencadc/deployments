"""Centralized Kubernetes configuration loader with caching.

This module provides a singleton pattern for loading Kubernetes configuration
to avoid repeated config loading across the codebase.
"""

from __future__ import annotations

import threading
from typing import Optional

from kubernetes import client, config
from kubernetes.client import ApiClient, BatchV1Api, CoreV1Api, CustomObjectsApi

from kueuer.utils.logging import logger


class KubernetesConfig:
    """Singleton Kubernetes configuration manager.
    
    This class ensures that Kubernetes configuration is loaded only once
    and provides cached access to commonly used API clients.
    
    Thread-safe implementation using double-checked locking pattern.
    """

    _instance: Optional[KubernetesConfig] = None
    _lock = threading.Lock()

    def __new__(cls) -> KubernetesConfig:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        
        self._initialized = True
        self._config_loaded = False
        self._api_client: Optional[ApiClient] = None
        self._core_v1: Optional[CoreV1Api] = None
        self._batch_v1: Optional[BatchV1Api] = None
        self._custom_objects: Optional[CustomObjectsApi] = None

    def _load_config(self) -> None:
        """Load Kubernetes configuration.
        
        Attempts to load from kubeconfig first, then falls back to
        in-cluster configuration if running inside a Kubernetes cluster.
        
        Raises:
            Exception: If neither kubeconfig nor in-cluster config is available.
        """
        if self._config_loaded:
            return

        try:
            config.load_kube_config()
            logger.debug("Loaded Kubernetes config from kubeconfig")
        except Exception as kubeconfig_error:
            try:
                config.load_incluster_config()
                logger.debug("Loaded Kubernetes config from in-cluster configuration")
            except Exception as incluster_error:
                logger.error(
                    "Failed to load Kubernetes config. "
                    "Kubeconfig error: %s. In-cluster error: %s",
                    kubeconfig_error,
                    incluster_error,
                )
                raise RuntimeError(
                    "Unable to load Kubernetes configuration. "
                    "Ensure kubeconfig is available or running in-cluster."
                ) from incluster_error

        self._config_loaded = True

    @property
    def api_client(self) -> ApiClient:
        """Get the Kubernetes API client."""
        self._load_config()
        if self._api_client is None:
            self._api_client = client.ApiClient()
        return self._api_client

    @property
    def core_v1(self) -> CoreV1Api:
        """Get the Core V1 API client for pods, services, namespaces, etc."""
        self._load_config()
        if self._core_v1 is None:
            self._core_v1 = client.CoreV1Api()
        return self._core_v1

    @property
    def batch_v1(self) -> BatchV1Api:
        """Get the Batch V1 API client for jobs and cronjobs."""
        self._load_config()
        if self._batch_v1 is None:
            self._batch_v1 = client.BatchV1Api()
        return self._batch_v1

    @property
    def custom_objects(self) -> CustomObjectsApi:
        """Get the Custom Objects API client for CRDs like Kueue resources."""
        self._load_config()
        if self._custom_objects is None:
            self._custom_objects = client.CustomObjectsApi()
        return self._custom_objects

    def ensure_loaded(self) -> None:
        """Ensure Kubernetes configuration is loaded.
        
        This is a convenience method for cases where you just need to
        ensure the config is loaded without accessing a specific API client.
        """
        self._load_config()

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance.
        
        This is primarily useful for testing to ensure a clean state
        between test runs.
        """
        with cls._lock:
            cls._instance = None


# Convenience function for getting the singleton instance
def get_k8s_config() -> KubernetesConfig:
    """Get the singleton Kubernetes configuration instance.
    
    Returns:
        KubernetesConfig: The singleton configuration instance.
    
    Example:
        >>> from kueuer.utils.k8s_config import get_k8s_config
        >>> k8s = get_k8s_config()
        >>> v1 = k8s.core_v1
        >>> namespaces = v1.list_namespace()
    """
    return KubernetesConfig()

