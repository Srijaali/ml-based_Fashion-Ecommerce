
import { API_URL } from "../api/api";

export function getImageUrl(path) {
    if (!path) return `${API_URL}/images/placeholder.jpg`;
    return `${API_URL}/images/${path}`;
}
