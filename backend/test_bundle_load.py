import logging
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("Starting service load...")
start = time.time()

from app.services.hybrid_recommendation_service import HybridRecommendationService

service = HybridRecommendationService()

end = time.time()
print(f'\nTotal startup time: {end-start:.2f}s')
print(f'CF ready: {service.is_ready()}')
print(f'Service status: {service.get_service_info()["status"]}')
