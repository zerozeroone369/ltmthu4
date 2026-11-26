"""Shared Tkinter session & status mixin for Duy Desktop Views (M02, M03)."""
from __future__ import annotations

from src.Modules.M01_Auth_TaiKhoan__TuAnh.Views.http_helper import run_async_tk


class SessionAwareViewMixin:
    """Resolve server_url/token from explicit callbacks, manual input, or ancestor tabs."""

    def _init_session_binding(
        self,
        *,
        server_url: str,
        auth_token: str,
        get_token,
        get_server_url,
    ) -> None:
        self.server_url = server_url or "http://127.0.0.1:8000"
        self.auth_token = auth_token
        self._get_token_cb = get_token
        self._get_server_url_cb = get_server_url

    def _resolve_ancestor(self, attr_names: tuple[str, ...]):
        cur = getattr(self, "master", None)
        while cur is not None:
            for name in attr_names:
                val = getattr(cur, name, None)
                if callable(val):
                    return val
            cur = getattr(cur, "master", None)
        return None

    def _server_url(self) -> str:
        if self._get_server_url_cb:
            return self._get_server_url_cb().strip().rstrip("/")
        inherited = self._resolve_ancestor(("_server_url", "get_server_url"))
        if inherited:
            val = (inherited() or "").strip().rstrip("/")
            if val:
                return val
        return self.server_url.strip().rstrip("/")

    def _token(self) -> str:
        if self._get_token_cb:
            return self._get_token_cb()
        manual = self.manual_token_var.get().strip() if hasattr(self, "manual_token_var") else ""
        if manual:
            return manual
        inherited = self._resolve_ancestor(("_token", "get_token"))
        if inherited:
            tok = inherited() or ""
            if tok:
                return tok
        return self.auth_token

    def _set_status(self, message: str, is_error: bool = False) -> None:
        self.status_lbl.config(text=message, foreground="#dc2626" if is_error else "#15803d")

    def _run_async(self, fn, on_done) -> None:
        run_async_tk(self, fn, on_done)
