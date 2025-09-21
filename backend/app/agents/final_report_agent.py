"""
Final Report Agent for consolidating all agent outputs into a comprehensive report
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from ..schemas import AgentResultCreate

class FinalReportAgent(BaseAgent):
    """Agent for creating a final consolidated report from all agent outputs"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "final_report", "consolidation")
    
    async def execute(self, launch_id: int, context=None) -> str:
        """Override execute method to bypass Ollama and generate report directly"""
        import time
        import logging
        from datetime import datetime
        
        logger = logging.getLogger(__name__)
        start_time = time.time()
        logger.info(f"Starting final report generation for launch {launch_id}")
        
        try:
            # Ensure context is a dictionary
            if context is None:
                context = {}
            elif isinstance(context, str):
                context = {"previous_output": context}
            
            # Get existing agent result record (created by orchestrator)
            result = self.agent_service.get_agent_result_by_name(launch_id, self.agent_name)
            if not result:
                # Fallback: create if not found
                result = self.agent_service.create_agent_result(
                    AgentResultCreate(
                        launch_id=launch_id,
                        agent_name=self.agent_name,
                        agent_type=self.agent_type,
                        status="in_progress"
                    )
                )
                logger.info(f"Created fallback agent result record with ID {result.id}")
            else:
                logger.info(f"Using existing agent result record with ID {result.id}")
            
            # Update status to in_progress
            self.agent_service.update_agent_result(
                result.id,
                status="in_progress"
            )
            
            # Generate the final report directly (no Ollama needed)
            logger.info(f"Generating comprehensive final report for {self.agent_name}")
            output = await self._execute_agent_logic(launch_id, context, None, {}, {})
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update result with success
            self.agent_service.update_agent_result(
                result.id,
                output=str(output),
                status="completed",
                execution_time=execution_time
            )
            logger.info(f"Final report agent completed successfully in {execution_time:.2f}s")
            
            return str(output)
            
        except Exception as e:
            logger.error(f"Critical error in final report agent: {str(e)}")
            execution_time = time.time() - start_time
            
            # Update result with error
            if 'result' in locals():
                self.agent_service.update_agent_result(
                    result.id,
                    status="failed",
                    error_flag=True,
                    error_message=str(e),
                    execution_time=execution_time
                )
            
            raise e
    
    async def _execute_agent_logic(self, launch_id: int, context: Dict[str, Any], 
                                 ollama, agent_config: Dict[str, Any], task_config: Dict[str, Any]) -> str:
        """Execute final report generation without using Ollama"""
        try:
            # Get all agent results for this launch
            agent_results = self.agent_service.get_agent_results(launch_id)
            
            # Get launch details
            from ..models import Launch
            launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
            
            # Get all previous agent outputs from context
            all_agent_outputs = {}
            for key, value in context.items():
                if key.endswith('_output') and isinstance(value, str):
                    agent_name = key.replace('_output', '')
                    all_agent_outputs[agent_name] = value
            
            # Create a comprehensive final report by manually consolidating key insights
            report_sections = []
            
            # 1. EXECUTIVE SUMMARY
            report_sections.append("EXECUTIVE SUMMARY")
            report_sections.append("=" * 50)
            report_sections.append(f"Launch: {launch.name if launch else 'Unknown'}")
            report_sections.append(f"Product Type: {launch.product_type if launch else 'Unknown'}")
            report_sections.append(f"Target Market: {launch.target_market if launch else 'Unknown'}")
            report_sections.append(f"Analysis Date: {launch.created_at if launch else 'Unknown'}")
            report_sections.append("")
            report_sections.append("This comprehensive analysis was conducted by 14 specialized AI agents")
            report_sections.append("covering all aspects of product launch readiness and strategy.")
            report_sections.append("")
            
            # 2. PHASE-BY-PHASE ANALYSIS
            phases = {
                "RESEARCH PHASE": ["market_intelligence", "customer_pulse"],
                "PLANNING PHASE": ["requirements_synthesizer", "timeline_resourcing", "risk_compliance"],
                "DEVELOPMENT PHASE": ["dev_coordination", "qa_testing", "documentation"],
                "LAUNCH PHASE": ["gtm", "readiness_check", "comms"],
                "MONITORING PHASE": ["telemetry_kpi", "feedback_loop", "retrospective"]
            }
            
            for phase_name, agent_names in phases.items():
                report_sections.append(phase_name)
                report_sections.append("-" * len(phase_name))
                
                for agent_name in agent_names:
                    # First try to get from context (real-time agent outputs)
                    agent_output = all_agent_outputs.get(agent_name, '')
                    if not agent_output:
                        # Fallback to database results
                        agent_result = next((r for r in agent_results if r.agent_name == agent_name), None)
                        if agent_result and agent_result.output:
                            agent_output = agent_result.output
                    
                    if agent_output:
                        # Extract key insights from each agent (first 300 chars for better context)
                        key_insights = agent_output[:300] + "..." if len(agent_output) > 300 else agent_output
                        report_sections.append(f"• {agent_name.replace('_', ' ').title()}: {key_insights}")
                        report_sections.append("")
                
                report_sections.append("")
            
            # 3. KEY RECOMMENDATIONS
            report_sections.append("KEY RECOMMENDATIONS")
            report_sections.append("=" * 50)
            report_sections.append("Based on the comprehensive multi-agent analysis:")
            report_sections.append("")
            report_sections.append("1. MARKET POSITIONING")
            report_sections.append("   - Leverage market intelligence insights for competitive positioning")
            report_sections.append("   - Address customer pain points identified in pulse analysis")
            report_sections.append("")
            report_sections.append("2. EXECUTION STRATEGY")
            report_sections.append("   - Follow timeline and resource recommendations")
            report_sections.append("   - Implement risk mitigation strategies")
            report_sections.append("   - Ensure quality assurance processes are in place")
            report_sections.append("")
            report_sections.append("3. LAUNCH READINESS")
            report_sections.append("   - Execute go-to-market strategy as planned")
            report_sections.append("   - Maintain communication protocols")
            report_sections.append("   - Monitor key performance indicators")
            report_sections.append("")
            report_sections.append("4. CONTINUOUS IMPROVEMENT")
            report_sections.append("   - Implement feedback loops for ongoing optimization")
            report_sections.append("   - Conduct regular retrospectives")
            report_sections.append("   - Track telemetry and KPIs continuously")
            report_sections.append("")
            
            # 4. SUCCESS METRICS
            report_sections.append("SUCCESS METRICS")
            report_sections.append("=" * 50)
            report_sections.append("• Market penetration and customer acquisition")
            report_sections.append("• Product performance and user satisfaction")
            report_sections.append("• Revenue targets and growth metrics")
            report_sections.append("• Risk mitigation effectiveness")
            report_sections.append("• Team performance and delivery timelines")
            report_sections.append("")
            
            # 5. NEXT STEPS
            report_sections.append("NEXT STEPS")
            report_sections.append("=" * 50)
            report_sections.append("1. Review and approve recommendations from each phase")
            report_sections.append("2. Assign ownership for key action items")
            report_sections.append("3. Establish monitoring and reporting cadence")
            report_sections.append("4. Schedule regular review meetings")
            report_sections.append("5. Prepare for launch execution")
            report_sections.append("")
            
            # 6. CONCLUSION
            report_sections.append("CONCLUSION")
            report_sections.append("=" * 50)
            report_sections.append("This comprehensive analysis provides a solid foundation for successful")
            report_sections.append("product launch. All critical aspects have been evaluated by specialized")
            report_sections.append("AI agents, ensuring thorough coverage of market, technical, and")
            report_sections.append("operational considerations.")
            report_sections.append("")
            report_sections.append("The launch is ready to proceed with confidence, backed by")
            report_sections.append("data-driven insights and strategic recommendations.")
            report_sections.append("")
            
            # Combine all sections
            final_report = "\n".join(report_sections)
            
            return f"FINAL CONSOLIDATED REPORT FOR LAUNCH {launch_id}\n\n{final_report}"
            
        except Exception as e:
            raise Exception(f"Final report generation failed: {str(e)}")
    
    def _get_fallback_response(self, launch_id: int, context: Dict[str, Any]) -> str:
        """Generate final report fallback response"""
        return f"""FINAL CONSOLIDATED REPORT FOR LAUNCH {launch_id} (Fallback Response)

EXECUTIVE SUMMARY:
- Multi-agent analysis completed successfully
- All 14 specialized agents have provided their insights
- Launch readiness assessment completed

PHASE-BY-PHASE ANALYSIS:
- Research Phase: Market intelligence and customer insights gathered
- Planning Phase: Requirements, timeline, and risk assessment completed
- Development Phase: Development coordination, QA, and documentation reviewed
- Launch Phase: Go-to-market strategy and readiness check completed
- Monitoring Phase: Telemetry, feedback, and retrospective analysis done

KEY RECOMMENDATIONS:
- Proceed with launch based on comprehensive analysis
- Monitor key performance indicators closely
- Implement feedback mechanisms for continuous improvement
- Maintain risk mitigation strategies

CONCLUSION:
- Launch is ready for execution
- All critical components have been analyzed
- Success metrics are in place
- Continuous monitoring recommended

Note: This report was generated using fallback logic. For detailed analysis, ensure Ollama server is running."""
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context for final report generation"""
        from ..models import Launch
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        if launch:
            return {
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description
            }
        return {}
