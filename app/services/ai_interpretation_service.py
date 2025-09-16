from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import openai
import json
from app.core.config import settings
from app.models.response import Response
from app.services.response_service import ResponseService

class AIIntepretationService:
    """AI 생성형 해석 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.response_service = ResponseService(db)
        
        # OpenAI 클라이언트 설정
        openai.api_key = settings.OPENAI_API_KEY
    
    def generate_interpretation(self, session_id: str, analysis_id: str, result_type: str, gender: str) -> Dict[str, str]:
        """결과에 따른 개인화된 해석 생성"""
        
        # 사용자의 응답 패턴 분석
        response_pattern = self._analyze_response_pattern(session_id, analysis_id)
        
        # 성향별 기본 템플릿 가져오기
        base_template = self._get_base_template(result_type, gender)
        
        # AI로 개인화된 해석 생성
        interpretations = {}
        
        for section, template in base_template.items():
            prompt = self._create_interpretation_prompt(
                result_type=result_type,
                gender=gender,
                section=section,
                template=template,
                response_pattern=response_pattern
            )
            
            interpretation = self._generate_with_ai(prompt)
            interpretations[section] = interpretation
        
        return interpretations
    
    def _analyze_response_pattern(self, session_id: str, analysis_id: str) -> Dict[str, Any]:
        """사용자의 응답 패턴 분석"""
        responses = self.response_service.get_responses_by_analysis(session_id, analysis_id)
        
        if not responses:
            return {}
        
        # 응답 패턴 분석
        pattern = {
            "total_responses": len(responses),
            "response_tendency": {},
            "answer_style": {},
            "consistency": 0
        }
        
        # 응답 선택 패턴 분석
        option1_count = sum(1 for r in responses if r.selected_option == 1)
        option2_count = sum(1 for r in responses if r.selected_option == 2)
        
        pattern["response_tendency"] = {
            "option1_ratio": option1_count / len(responses) if responses else 0,
            "option2_ratio": option2_count / len(responses) if responses else 0,
            "dominant_choice": "option1" if option1_count > option2_count else "option2"
        }
        
        # 일관성 분석 (연속된 같은 선택)
        consistency_count = 0
        for i in range(1, len(responses)):
            if responses[i].selected_option == responses[i-1].selected_option:
                consistency_count += 1
        
        pattern["consistency"] = consistency_count / (len(responses) - 1) if len(responses) > 1 else 0
        
        return pattern
    
    def _get_base_template(self, result_type: str, gender: str) -> Dict[str, str]:
        """성향별 기본 템플릿 가져오기"""
        templates = {
            "성격 특징": f"""
당신은 {result_type} 성향의 {gender}입니다. 
기본적인 성향 특성을 설명하면서, 개인적인 특색도 언급해주세요.
- 성향의 핵심 특징 (2-3줄)
- 개인적인 특색 (1-2줄)
- 매력 포인트 (1줄)
""",
            "인간관계": f"""
{result_type} 성향의 {gender}로서의 인간관계 스타일을 설명해주세요.
- 친구들과의 관계 방식 (2-3줄)
- 소통 스타일 (1-2줄)
- 깊은 관계 형성 방법 (1줄)
""",
            "연애 스타일": f"""
{result_type} 성향의 {gender}로서의 연애 스타일을 설명해주세요.
- 연애 접근 방식 (2-3줄)
- 매력적인 면 (1-2줄)
- 이상적인 관계 (1줄)
"""
        }
        
        return templates
    
    def _create_interpretation_prompt(self, result_type: str, gender: str, section: str, 
                                    template: str, response_pattern: Dict[str, Any]) -> str:
        """해석 생성 프롬프트 생성"""
        
        prompt = f"""
당신은 성향분석 전문가입니다. 사용자의 응답 패턴을 분석하여 개인화된 해석을 제공해주세요.

**분석 정보:**
- 결과 유형: {result_type}
- 성별: {gender}
- 섹션: {section}

**사용자 응답 패턴:**
- 총 응답 수: {response_pattern.get('total_responses', 0)}
- 응답 경향: {response_pattern.get('response_tendency', {}).get('dominant_choice', 'unknown')}
- 일관성: {response_pattern.get('consistency', 0):.2f}

**해석 요구사항:**
{template}

**스타일 가이드:**
- MZ 세대가 좋아하는 친근한 톤앤매너
- 이모지 적절히 활용 (2-3개)
- 2-4줄로 간결하게
- 개인화된 내용 포함
- 같은 성향이면 비슷한 방향으로 해석

**제약사항:**
- 같은 성향이면 기본적인 방향은 유사해야 함
- 개인화는 세부적인 표현과 예시로만
- 너무 극단적이거나 상이한 해석 금지

해석을 생성해주세요:
"""
        
        return prompt
    
    def _generate_with_ai(self, prompt: str) -> str:
        """AI로 해석 생성"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 성향분석 전문가입니다. 친근하고 정확한 해석을 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7,  # 적당한 창의성
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI 해석 생성 실패: {e}")
            return "해석을 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def generate_batch_interpretations(self, session_id: str, analysis_id: str, 
                                     result_type: str, gender: str) -> Dict[str, str]:
        """일괄 해석 생성 (성능 최적화)"""
        
        # 응답 패턴 분석
        response_pattern = self._analyze_response_pattern(session_id, analysis_id)
        
        # 모든 섹션을 한 번에 생성하는 프롬프트
        prompt = self._create_batch_prompt(result_type, gender, response_pattern)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 성향분석 전문가입니다. 구조화된 해석을 JSON 형태로 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7,
                top_p=0.9
            )
            
            content = response.choices[0].message.content.strip()
            
            # JSON 파싱 시도
            try:
                interpretations = json.loads(content)
                return interpretations
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 해석 반환
                return self._get_fallback_interpretations(result_type, gender)
                
        except Exception as e:
            print(f"AI 일괄 해석 생성 실패: {e}")
            return self._get_fallback_interpretations(result_type, gender)
    
    def _create_batch_prompt(self, result_type: str, gender: str, response_pattern: Dict[str, Any]) -> str:
        """일괄 해석 생성 프롬프트"""
        
        prompt = f"""
당신은 성향분석 전문가입니다. 사용자의 응답 패턴을 분석하여 개인화된 해석을 JSON 형태로 제공해주세요.

**분석 정보:**
- 결과 유형: {result_type}
- 성별: {gender}
- 응답 패턴: {json.dumps(response_pattern, ensure_ascii=False, indent=2)}

**요구사항:**
다음 3개 섹션에 대한 해석을 JSON 형태로 생성해주세요:

1. "성격 특징": {result_type} 성향의 핵심 특징과 개인적 특색 (2-4줄)
2. "인간관계": 친구들과의 관계 방식과 소통 스타일 (2-4줄)  
3. "연애 스타일": 연애 접근 방식과 매력적인 면 (2-4줄)

**스타일 가이드:**
- MZ 세대 친근한 톤앤매너
- 이모지 2-3개 적절히 활용
- 같은 성향이면 비슷한 방향으로 해석
- 개인화는 세부 표현으로만

**응답 형식:**
```json
{{
  "성격 특징": "해석 내용",
  "인간관계": "해석 내용", 
  "연애 스타일": "해석 내용"
}}
```

해석을 생성해주세요:
"""
        
        return prompt
    
    def _get_fallback_interpretations(self, result_type: str, gender: str) -> Dict[str, str]:
        """AI 생성 실패 시 기본 해석 반환"""
        return {
            "성격 특징": f"당신은 {result_type} 성향의 {gender}입니다! 🎭\n독특한 매력과 개성을 가지고 있어요.\n주변 사람들이 당신의 특별함을 인정할 거예요.",
            "인간관계": f"친구들과의 관계에서 {result_type} 특성이 잘 드러나요! 👥\n당신만의 방식으로 사람들과 소통해요.\n진짜 친한 친구들과는 깊은 유대감을 형성해요.",
            "연애 스타일": f"연애에서도 {result_type} 성향이 특별하게 나타나요! 💕\n당신만의 매력으로 상대방을 사로잡아요.\n진정한 사랑을 찾을 때까지 기다리는 타입이에요."
        }
