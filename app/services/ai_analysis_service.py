from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import uuid
import json

from app.models.ai_analysis import AIAnalysisSession, AIAnalysisQuestion, AIAnalysisResult
from app.services.ai_interpretation_service import AIIntepretationService
from openai import OpenAI
from app.core.config import settings

class AIAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_interpretation_service = AIIntepretationService(db)
        
        # OpenAI 클라이언트 설정
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def start_analysis(self, analysis_id: str, session_id: str, gender: str) -> Dict[str, Any]:
        """
        AI 분석 시작 - 첫 번째 질문 생성
        """
        try:
            # 세션 생성
            session = AIAnalysisSession(
                session_id=session_id,
                analysis_id=analysis_id,
                gender=gender,
                status="in_progress"
            )
            self.db.add(session)
            self.db.flush()  # ID를 즉시 생성하기 위해 flush
            
            print(f"Created session with ID: {session.id}")
            
            # 첫 번째 질문 생성
            first_question = await self._generate_first_question(analysis_id, gender, 1)
            
            # 질문 저장
            question = AIAnalysisQuestion(
                session_id=session.id,
                question_index=1,
                question_text=first_question["question_text"],
                option_1=first_question["option_1"],
                option_2=first_question["option_2"]
            )
            self.db.add(question)
            
            self.db.commit()
            
            return {
                "question_id": question.id,
                "question_text": first_question["question_text"],
                "option_1": first_question["option_1"],
                "option_2": first_question["option_2"],
                "hint": first_question["hint"],
                "is_complete": False
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def submit_answer(self, session_id: str, question_id: str, answer: int, gender: str) -> Dict[str, Any]:
        """
        질문 답변 제출 - 다음 질문 생성 또는 분석 완료
        """
        try:
            # 세션 조회
            session = self.db.query(AIAnalysisSession).filter(AIAnalysisSession.session_id == session_id).first()
            if not session:
                raise ValueError("Session not found")
            
            # 현재 질문 조회
            current_question = self.db.query(AIAnalysisQuestion).filter(AIAnalysisQuestion.id == question_id).first()
            if not current_question:
                raise ValueError("Question not found")
            
            # 답변 저장
            if not session.answers:
                session.answers = []
            session.answers.append({
                "question_id": question_id,
                "answer": answer,
                "question_index": current_question.question_index
            })
            
            # 다음 질문 생성 또는 분석 완료 확인
            next_question_order = current_question.question_index + 1
            
            if next_question_order > 12:  # 12개 질문 완료
                # 분석 완료 처리
                result = await self._complete_analysis(session_id, gender)
                return result
            else:
                # 다음 질문 생성
                next_question = await self._generate_next_question(session.analysis_id, gender, next_question_order, session_id)
                
                # 다음 질문 저장
                question = AIAnalysisQuestion(
                    session_id=session.id,
                    question_index=next_question_order,
                    question_text=next_question["question_text"],
                    option_1=next_question["option_1"],
                    option_2=next_question["option_2"]
                )
                self.db.add(question)
                self.db.flush()  # ID 생성을 위해 flush
                
                self.db.commit()
                
                return {
                    "question_id": question.id,
                    "question_text": next_question["question_text"],
                    "option_1": next_question["option_1"],
                    "option_2": next_question["option_2"],
                    "hint": next_question["hint"],
                    "is_complete": False
                }
                
        except Exception as e:
            self.db.rollback()
            print(f"submit_answer 에러: {e}")
            print(f"에러 타입: {type(e)}")
            import traceback
            traceback.print_exc()
            raise e
    
    async def _generate_first_question(self, analysis_id: str, gender: str, order: int = 1) -> Dict[str, str]:
        """
        첫 번째 질문 생성 (AI 사용)
        """
        try:
            if analysis_id == "ai-bdsm-analysis":
                analysis_type = "BDSM 성향 분석"
                personality_types = "도미넌트, 서브, 스위치"
                
                prompt = f"""
🎭 당신은 MZ 세대를 위한 재미있는 스토리텔러입니다! {gender} 사용자를 위한 첫 번째 질문을 생성해주세요.

✨ 재미있는 스토리텔링 요구사항:
1. 🎬 드라마틱한 상황 설정: "갑자기 이런 일이 벌어졌어요!", "그런데 순간..." 같은 긴장감
2. 😂 유머와 재미 요소: 웃긴 상황이나 예상치 못한 전개
3. 🎯 감정 몰입: "심장이 두근두근", "머리가 하얘져요" 같은 생생한 감정 표현
4. 🔥 MZ 트렌드 반영: 인스타, 유튜브, 쇼츠, 카페, 브런치 등 MZ가 사는 현실
5. 💫 반전과 재미: "그런데 알고 보니...", "하지만 놀랍게도..." 같은 반전 요소
6. 🎪 상상력 가득: 평범한 일상에 판타지나 코미디 요소 추가

분석할 성향: {personality_types}

다음 JSON 형식으로 응답해주세요:
{{
    "question_text": "🎭 드라마틱하고 재미있는 스토리텔링 질문 (이모지 포함)",
    "option_1": "첫 번째 선택지 (구체적이고 재미있는 행동)",
    "option_2": "두 번째 선택지 (구체적이고 재미있는 행동)",
    "hint": "🎪 친근하고 재미있는 힌트 메시지 (이모지 포함)"
}}
"""
            else:  # ai-egen-analysis
                analysis_type = "에겐/테토 성향 분석"
                personality_types = "에겐, 테토"
                
                prompt = f"""
당신은 성격 심리 테스트 질문을 만드는 전문가입니다.
목표는 '에겐/테토 성향 분석'을 위한 질문을 만드는 것입니다.

요구사항:
1. 질문은 MZ 세대가 공감할 수 있도록 유머러스하고 일상적인 상황 중심으로 만들어라.
2. 각 질문은 하나의 축(에겐 vs 테토, 액티브 vs 리플렉트, 플랜 vs 플로우)을 반영해야 한다.
3. 각 질문은 A/B 두 가지 답변을 제공한다.
   - A, B는 직관적이고 대조적으로 작성할 것.
   - 답변에는 에겐/테토 또는 액티브/리플렉트/플랜/플로우 중 어떤 성향을 가리키는지 고려할 것.
4. {gender} 사용자가 공감할 수 있는 현실적인 상황을 설정할 것.
5. 유머와 재미를 포함하되 성향 분석에 유효한 질문이 되
도록 할 것.

출력 형식 (JSON):
{{
    "question_text": "일상적이고 재미있는 상황 질문",
    "option_1": "첫 번째 선택지 (에겐/액티브/플랜 성향)",
    "option_2": "두 번째 선택지 (테토/리플렉트/플로우 성향)",
    "hint": "친근하고 재미있는 힌트 메시지 (이모지 포함)"
}}

예시:
{{
    "question_text": "🎭 약속 장소에 30분 일찍 도착했는데, 친구가 늦을 것 같다고 연락이 왔어요. 이때 당신은?",
    "option_1": "근처 카페에서 사람 구경하면서 기다리고, 새로운 장소도 탐험해봐요",
    "option_2": "휴대폰으로 일정 정리하면서 차분히 준비하고 기다려요",
    "hint": "에겐/테토 성향을 재미있게 분석하고 있어요! 🎭"
}}
"""

            if analysis_id == "ai-bdsm-analysis":
                system_message = "당신은 MZ 세대를 위한 재미있는 스토리텔러입니다. 일상의 평범한 상황을 흥미진진한 이야기로 만들어서 사람들의 진짜 성향을 끌어내는 전문가예요. 유머와 감정이 가득한 질문을 만들어주세요."
            else:  # ai-egen-analysis
                system_message = "당신은 성격 심리 테스트 전문가입니다. 에겐/테토 성향을 정확하게 분석할 수 있는 유효하고 재미있는 질문을 만드는 것이 목표입니다. MZ 세대가 공감할 수 있는 일상적인 상황을 바탕으로 하되, 성향 분석에 도움이 되는 질문을 만들어주세요."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI 질문 생성 오류: {e}")
            # AI 생성 실패 시 에러 반환 (목업 질문 사용 안함)
            raise Exception(f"AI 질문 생성에 실패했습니다: {str(e)}")
    
    async def _generate_next_question(self, analysis_id: str, gender: str, order: int, session_id: str = None) -> Dict[str, str]:
        """
        다음 질문 생성 (AI 사용, 이전 답변 맥락 고려)
        """
        try:
            # 이전 답변들 가져오기
            previous_answers = []
            if session_id:
                session = self.db.query(AIAnalysisSession).filter(AIAnalysisSession.session_id == session_id).first()
                if session and session.answers:
                    previous_answers = session.answers
            
            if analysis_id == "ai-bdsm-analysis":
                analysis_type = "BDSM 성향 분석"
                personality_types = "도미넌트, 서브, 스위치"
                
                # 이전 답변 맥락 추가
                context = ""
                if previous_answers:
                    context = f"\n이전 답변들: {previous_answers[-3:]}"  # 최근 3개 답변만
                
                prompt = f"""
🎪 당신은 MZ 세대를 위한 재미있는 스토리텔러입니다! {gender} 사용자를 위한 {order}번째 질문을 생성해주세요.

🎭 더욱 재미있는 스토리텔링 요구사항:
1. 🎬 새로운 드라마틱한 상황: 이전 질문과 완전히 다른 장르나 상황으로!
2. 😂 더 웃긴 요소: "갑자기 이런 일이?", "그런데 알고 보니..." 같은 반전
3. 🎯 감정 몰입 극대화: "심장이 터질 것 같아요", "손이 떨려요" 같은 생생한 표현
4. 🔥 MZ 트렌드 업그레이드: 인스타, 틱톡, 쇼츠, 브런치, 카페, 쇼핑몰 등
5. 💫 상상력 폭발: "만약에 이런 일이 일어난다면?", "갑자기 마법이 생긴다면?"
6. 🎪 재미있는 캐릭터: "친구가 갑자기 이상해져서...", "알바생이 말을 걸어와서..."

분석할 성향: {personality_types}
질문 순서: {order}/12{context}

다음 JSON 형식으로 응답해주세요:
{{
    "question_text": "🎭 드라마틱하고 재미있는 스토리텔링 질문 (이모지 포함)",
    "option_1": "첫 번째 선택지 (구체적이고 재미있는 행동)",
    "option_2": "두 번째 선택지 (구체적이고 재미있는 행동)",
    "hint": "🎪 친근하고 재미있는 힌트 메시지 (이모지 포함, 성향 분석 상태)"
}}
"""
            else:  # ai-egen-analysis
                analysis_type = "에겐/테토 성향 분석"
                personality_types = "에겐, 테토"
                
                # 이전 답변 맥락 추가
                context = ""
                if previous_answers:
                    context = f"\n이전 답변들: {previous_answers[-3:]}"  # 최근 3개 답변만
                
                prompt = f"""
당신은 성격 심리 테스트 질문을 만드는 전문가입니다.
목표는 '에겐/테토 성향 분석'을 위한 {order}번째 질문을 만드는 것입니다.

요구사항:
1. 질문은 MZ 세대가 공감할 수 있도록 유머러스하고 일상적인 상황 중심으로 만들어라.
2. 각 질문은 하나의 축(에겐 vs 테토, 액티브 vs 리플렉트, 플랜 vs 플로우)을 반영해야 한다.
3. 이전 질문과는 다른 새로운 상황이나 맥락을 설정할 것.
4. 각 질문은 A/B 두 가지 답변을 제공한다.
   - A, B는 직관적이고 대조적으로 작성할 것.
   - 답변에는 에겐/테토 또는 액티브/리플렉트/플랜/플로우 중 어떤 성향을 가리키는지 고려할 것.
5. {gender} 사용자가 공감할 수 있는 현실적인 상황을 설정할 것.
6. 유머와 재미를 포함하되 성향 분석에 유효한 질문이 되도록 할 것.

질문 순서: {order}/12{context}

출력 형식 (JSON):
{{
    "question_text": "일상적이고 재미있는 상황 질문 (이전과 다른 새로운 맥락)",
    "option_1": "첫 번째 선택지 (에겐/액티브/플랜 성향)",
    "option_2": "두 번째 선택지 (테토/리플렉트/플로우 성향)",
    "hint": "친근하고 재미있는 힌트 메시지 (이모지 포함)"
}}

예시:
{{
    "question_text": "🎭 새로운 프로젝트를 시작하게 되었는데, 팀장이 '자유롭게 해도 돼'라고 했어요. 이때 당신은?",
    "option_1": "바로 창의적인 아이디어를 제안하고 팀을 이끌어가고 싶어요",
    "option_2": "먼저 팀원들의 의견을 들어보고 방향을 정하고 싶어요",
    "hint": "리더십 스타일을 재미있게 분석하고 있어요! 👑"
}}
"""

            if analysis_id == "ai-bdsm-analysis":
                system_message = "당신은 MZ 세대를 위한 재미있는 스토리텔러입니다! 매번 새로운 상황과 재미있는 스토리로 사람들을 놀라게 만드는 전문가예요. 유머와 감정, 반전이 가득한 질문을 만들어주세요."
            else:  # ai-egen-analysis
                system_message = "당신은 성격 심리 테스트 전문가입니다. 에겐/테토 성향을 정확하게 분석할 수 있는 유효하고 재미있는 질문을 만드는 것이 목표입니다. MZ 세대가 공감할 수 있는 일상적인 상황을 바탕으로 하되, 성향 분석에 도움이 되는 질문을 만들어주세요."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI 질문 생성 오류: {e}")
            # AI 생성 실패 시 에러 반환 (목업 질문 사용 안함)
            raise Exception(f"AI 질문 생성에 실패했습니다: {str(e)}")
    
    async def _complete_analysis(self, session_id: str, gender: str) -> Dict[str, Any]:
        """
        분석 완료 처리
        """
        try:
            # 임시 결과 생성 (실제로는 AI 분석 결과를 사용해야 함)
            result_data = {
                "result_type": "AC-RF-EG_TT-PL_FL",
                "title": "에겐 성향",
                "description": "당신은 독창적이고 개성적인 에겐 성향입니다!",
                "interpretations": {
                    "성격 특징": "당신은 에겐 성향의 소유자예요! 🎭\n독창적이고 개성적인 사고방식을 가지고 있어요.\n주변 사람들이 당신의 독특함에 매력을 느낄 거예요.",
                    "인간관계": "친구들과의 관계에서 에겐 특성이 잘 드러나요! 👥\n당신만의 독특한 방식으로 사람들과 소통해요.\n진짜 친한 친구들과는 더욱 깊은 유대감을 형성해요.",
                    "연애 스타일": "연애에서도 에겐 성향이 특별하게 나타나요! 💕\n당신만의 독특한 매력으로 상대방을 사로잡아요.\n진정한 사랑을 찾을 때까지 기다리는 타입이에요."
                },
                "is_complete": True
            }
            
            # 결과 저장
            result = AIAnalysisResult(
                session_id=session.id,
                result_type=result_data["result_type"],
                title=result_data["title"],
                description=result_data["description"]
            )
            self.db.add(result)
            
            # 세션 상태 업데이트
            session = self.db.query(AIAnalysisSession).filter(AIAnalysisSession.session_id == session_id).first()
            if session:
                session.status = "completed"
            
            self.db.commit()
            
            return result_data
            
        except Exception as e:
            self.db.rollback()
            raise e
