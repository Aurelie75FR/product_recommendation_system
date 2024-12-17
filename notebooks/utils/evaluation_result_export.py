import pandas as pd
import os

class EvaluationResultsExporter:
    """
    Classe pour formater et exporter les résultats d'évaluation pour Flourish
    """
    def __init__(self, evaluation_results, output_dir='flourish_evaluation/'):
        self.results = evaluation_results
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def prepare_diversity_metrics(self):
        """
        Prépare le dataset des métriques de diversité
        """
        diversity_data = pd.DataFrame({
            'Metric': [
                'Diversité des catégories',
                'Ratio de gamme de prix',
                'Distance de prix',
                'Écart de notation'
            ],
            'Value': [
                self.results['diversity']['category_diversity'],
                self.results['diversity']['price_range_ratio'],
                self.results['diversity']['price_distance'],
                self.results['diversity']['rating_spread']
            ],
            'Description': [
                'Variété des catégories recommandées',
                'Étendue des prix recommandés',
                'Différence moyenne de prix',
                'Écart entre les notes min et max'
            ]
        })
        
        diversity_data.to_csv(f'{self.output_dir}diversity_metrics.csv', index=False)
        return diversity_data
    
    def prepare_relevance_metrics(self):
        """
        Prépare le dataset des métriques de pertinence
        """
        relevance_data = pd.DataFrame({
            'Metric': [
                'Note moyenne',
                'Nombre moyen d\'avis',
                'Note minimale',
                'Note pondérée'
            ],
            'Value': [
                self.results['relevance']['avg_rating'],
                self.results['relevance']['avg_reviews'],
                self.results['relevance']['min_rating'],
                self.results['relevance']['weighted_rating']
            ],
            'Description': [
                'Moyenne des notes des produits recommandés',
                'Moyenne du nombre d\'avis',
                'Note la plus basse recommandée',
                'Note moyenne pondérée par le nombre d\'avis'
            ]
        })
        
        relevance_data.to_csv(f'{self.output_dir}relevance_metrics.csv', index=False)
        return relevance_data
    
    def prepare_coverage_metrics(self):
        """
        Prépare le dataset des métriques de couverture
        """
        coverage_data = pd.DataFrame({
            'Metric': [
                'Couverture des catégories',
                'Couverture des prix',
                'Ratio d\'items uniques',
                'Taux de succès'
            ],
            'Value': [
                self.results['coverage']['category_coverage'],
                self.results['coverage']['price_range_coverage'],
                self.results['coverage']['unique_items_ratio'],
                self.results['coverage']['success_rate']
            ],
            'Description': [
                'Proportion des catégories couvertes',
                'Proportion de la gamme de prix couverte',
                'Ratio de recommandations uniques',
                'Taux de recommandations réussies'
            ]
        })
        
        coverage_data.to_csv(f'{self.output_dir}coverage_metrics.csv', index=False)
        return coverage_data
    
    def prepare_overall_performance(self):
        """
        Prépare un dataset résumant la performance globale
        """
        # Calculer les moyennes par catégorie
        avg_diversity = sum(self.results['diversity'].values()) / len(self.results['diversity'])
        avg_relevance = sum(self.results['relevance'].values()) / len(self.results['relevance'])
        avg_coverage = sum(self.results['coverage'].values()) / len(self.results['coverage'])
        
        performance_data = pd.DataFrame({
            'Category': ['Diversité', 'Pertinence', 'Couverture'],
            'Score': [avg_diversity, avg_relevance, avg_coverage],
            'Color': ['#FF9999', '#99FF99', '#9999FF']  # Couleurs pour Flourish
        })
        
        performance_data.to_csv(f'{self.output_dir}overall_performance.csv', index=False)
        return performance_data
    
    def export_all_metrics(self):
        """
        Exporte tous les datasets
        """
        datasets = {
            'diversity': self.prepare_diversity_metrics(),
            'relevance': self.prepare_relevance_metrics(),
            'coverage': self.prepare_coverage_metrics(),
            'overall': self.prepare_overall_performance()
        }
        return datasets