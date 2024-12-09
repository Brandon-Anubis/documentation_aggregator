# src/utils/marketing_detector.py
from spacy import load
from spacy.language import Language
from spacy.tokens import Doc, Span
import en_core_web_lg

class MarketingContentDetector:
    def __init__(self):
        self.nlp = load("en_core_web_lg")
        
        # Register custom component
        if not Language.has_factory("marketing_detector"):
            Language.factory("marketing_detector", func=self.create_marketing_detector)
            self.nlp.add_pipe("marketing_detector", last=True)
    
    @staticmethod
    def create_marketing_detector(nlp: Language, name: str):
        return MarketingDetectorComponent(nlp)
    
    def is_marketing_section(self, text: str) -> bool:
        doc = self.nlp(text)
        return doc._.is_marketing

class MarketingDetectorComponent:
    def __init__(self, nlp: Language):
        Doc.set_extension("is_marketing", default=False, force=True)
        Doc.set_extension("marketing_score", default=0.0, force=True)
        
    def __call__(self, doc: Doc) -> Doc:
        # Calculate marketing score based on multiple factors
        promotional_score = self._analyze_promotional_content(doc)
        structural_score = self._analyze_structure(doc)
        semantic_score = self._analyze_semantics(doc)
        
        # Combine scores with weights
        total_score = (
            promotional_score * 0.3 + 
            structural_score * 0.4 + 
            semantic_score * 0.3
        )
        
        doc._.marketing_score = total_score
        doc._.is_marketing = total_score > 0.6
        return doc
    
    def _analyze_promotional_content(self, doc: Doc) -> float:
        if len(doc) == 0:
            return 0.0

        cta_verbs = [token for token in doc if token.pos_ == "VERB" and token.dep_ in ["ROOT", "advcl"]]
        future_indicators = len([token for token in doc if token.lemma_ in ["will", "shall", "going"]])
        
        return min((len(cta_verbs) + future_indicators) / len(doc), 1.0)
    
    def _analyze_structure(self, doc: Doc) -> float:
        if len(doc) == 0:
            return 0.0

        has_contact_info = any(ent.label_ == "CONTACT" for ent in doc.ents)
        has_urls = any(token.like_url for token in doc)
        has_numbers = any(token.like_num for token in doc)
        
        structural_indicators = sum([has_contact_info, has_urls, has_numbers])
        return structural_indicators / 3.0
    
    def _analyze_semantics(self, doc: Doc) -> float:
        if len(doc) == 0:
            return 0.0

        promotional_ents = [ent for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "MONEY", "PERCENT"]]
        marketing_phrases = len([chunk for chunk in doc.noun_chunks if self._is_promotional_phrase(chunk)])
        
        return min((len(promotional_ents) + marketing_phrases) / len(doc), 1.0)
    
    def _is_promotional_phrase(self, chunk: Span) -> bool:
        promotional_indicators = {
            "feature", "benefit", "solution", "service",
            "product", "offer", "deal", "price"
        }
        return any(token.lemma_.lower() in promotional_indicators for token in chunk)
