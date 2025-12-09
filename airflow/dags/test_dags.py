"""
Test script to verify DAGs can be parsed correctly
"""
import unittest
import os
import sys

# Add the dags directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

class TestDAGs(unittest.TestCase):
    
    def test_user_item_interactions_dag(self):
        """Test that user_item_interactions DAG can be imported"""
        try:
            import user_item_interactions
            self.assertTrue(hasattr(user_item_interactions, 'dag'))
            self.assertEqual(user_item_interactions.dag.dag_id, 'user_item_interactions')
        except Exception as e:
            self.fail(f"Failed to import user_item_interactions DAG: {e}")
    
    def test_articles_content_dag(self):
        """Test that articles_content DAG can be imported"""
        try:
            import articles_content
            self.assertTrue(hasattr(articles_content, 'dag'))
            self.assertEqual(articles_content.dag.dag_id, 'articles_content')
        except Exception as e:
            self.fail(f"Failed to import articles_content DAG: {e}")
    
    def test_articles_embeddings_dag(self):
        """Test that articles_embeddings DAG can be imported"""
        try:
            import articles_embeddings
            self.assertTrue(hasattr(articles_embeddings, 'dag'))
            self.assertEqual(articles_embeddings.dag.dag_id, 'articles_embeddings')
        except Exception as e:
            self.fail(f"Failed to import articles_embeddings DAG: {e}")
    
    def test_customer_features_dag(self):
        """Test that customer_features DAG can be imported"""
        try:
            import customer_features
            self.assertTrue(hasattr(customer_features, 'dag'))
            self.assertEqual(customer_features.dag.dag_id, 'customer_features')
        except Exception as e:
            self.fail(f"Failed to import customer_features DAG: {e}")
    
    def test_timeseries_dag(self):
        """Test that timeseries DAG can be imported"""
        try:
            import timeseries
            self.assertTrue(hasattr(timeseries, 'dag'))
            self.assertEqual(timeseries.dag.dag_id, 'timeseries')
        except Exception as e:
            self.fail(f"Failed to import timeseries DAG: {e}")
    
    def test_reviews_nlp_dag(self):
        """Test that reviews_nlp DAG can be imported"""
        try:
            import reviews_nlp
            self.assertTrue(hasattr(reviews_nlp, 'dag'))
            self.assertEqual(reviews_nlp.dag.dag_id, 'reviews_nlp')
        except Exception as e:
            self.fail(f"Failed to import reviews_nlp DAG: {e}")
    
    def test_events_and_funnels_dag(self):
        """Test that events_and_funnels DAG can be imported"""
        try:
            import events_and_funnels
            self.assertTrue(hasattr(events_and_funnels, 'dag'))
            self.assertEqual(events_and_funnels.dag.dag_id, 'events_and_funnels')
        except Exception as e:
            self.fail(f"Failed to import events_and_funnels DAG: {e}")

if __name__ == '__main__':
    unittest.main()