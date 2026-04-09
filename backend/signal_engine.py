import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class SignalAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"

dataclass
class Signal:
    asset: str
    action: SignalAction
    probability: float  # 0-100
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    reasons: List[str]
    strength_level: str  # Weak, Moderate, Strong, Institutional

class SignalEngine:
    """Multi-layer scoring engine for trading signals"""
    
    def __init__(self):
        self.min_score_threshold = 70  # Only generate alerts >= 70%
        self.weights = {
            'trend': 0.25,
            'pullback': 0.20,
            'momentum': 0.20,
            'smart_money': 0.20,
            'market_state': 0.15
        }
    
    def calculate_signal(self, market_data: Dict) -> Signal | None:
        """
        Calculate comprehensive signal probability score
        Returns Signal object or None if score < 70%
        """
        scores = {}
        reasons = []
        
        # Layer 1: Trend Analysis (25%)
        trend_score, trend_reasons = self._analyze_trend(market_data)
        scores['trend'] = trend_score
        reasons.extend(trend_reasons)
        
        # Layer 2: Pullback Analysis (20%)
        pullback_score, pullback_reasons = self._analyze_pullback(market_data)
        scores['pullback'] = pullback_score
        reasons.extend(pullback_reasons)
        
        # Layer 3: Momentum Analysis (20%)
        momentum_score, momentum_reasons = self._analyze_momentum(market_data)
        scores['momentum'] = momentum_score
        reasons.extend(momentum_reasons)
        
        # Layer 4: Smart Money Analysis (20%)
        smart_money_score, smart_money_reasons = self._analyze_smart_money(market_data)
        scores['smart_money'] = smart_money_score
        reasons.extend(smart_money_reasons)
        
        # Layer 5: Market State (15%)
        market_state_score, market_state_reasons = self._analyze_market_state(market_data)
        scores['market_state'] = market_state_score
        reasons.extend(market_state_reasons)
        
        # Calculate weighted probability
        probability = sum(scores[key] * self.weights[key] for key in scores)
        
        # Determine signal action
        action = self._determine_action(market_data, probability)
        
        # Only generate signal if probability >= threshold
        if probability < self.min_score_threshold:
            return None
        
        # Determine strength level
        strength_level = self._calculate_strength_level(probability)
        
        # Extract entry, SL, TP
        entry_price = market_data.get('current_price', 0)
        stop_loss = self._calculate_stop_loss(market_data, action)
        take_profit = self._calculate_take_profit(market_data, action)
        
        return Signal(
            asset=market_data.get('asset', 'UNKNOWN'),
            action=action,
            probability=probability,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timestamp=datetime.now(),
            reasons=reasons,
            strength_level=strength_level
        )
    
    def _analyze_trend(self, market_data: Dict) -> Tuple[float, List[str]]:
        """
        Trend Layer (25%): EMA 50/200 crossover and market structure (HH/HL)
        """
        score = 0
        reasons = []
        
        ema_50 = market_data.get('ema_50', 0)
        ema_200 = market_data.get('ema_200', 0)
        current_price = market_data.get('current_price', 0)
        
        # EMA Crossover
        if ema_50 > ema_200 and current_price > ema_50:
            score += 50
            reasons.append("EMA 50/200 Bullish Crossover")
        elif ema_50 < ema_200 and current_price < ema_50:
            score += 50
            reasons.append("EMA 50/200 Bearish Crossover")
        
        # Market Structure (HH/HL)
        higher_high = market_data.get('higher_high', False)
        higher_low = market_data.get('higher_low', False)
        
        if higher_high and higher_low:
            score += 50
            reasons.append("Higher High/Higher Low Structure")
        
        return min(score, 100), reasons
    
    def _analyze_pullback(self, market_data: Dict) -> Tuple[float, List[str]]:
        """
        Pullback Layer (20%): Fibonacci 61.8 levels and EMA 20 touches
        """
        score = 0
        reasons = []
        
        fib_61_8 = market_data.get('fibonacci_61_8', 0)
        current_price = market_data.get('current_price', 0)
        ema_20 = market_data.get('ema_20', 0)
        
        # Fibonacci 61.8 bounce
        if abs(current_price - fib_61_8) / fib_61_8 < 0.02:  # Within 2%
            score += 50
            reasons.append("Fibonacci 61.8 Level Touch")
        
        # EMA 20 touch
        if abs(current_price - ema_20) / ema_20 < 0.01:  # Within 1%
            score += 50
            reasons.append("EMA 20 Touch/Bounce")
        
        return min(score, 100), reasons
    
    def _analyze_momentum(self, market_data: Dict) -> Tuple[float, List[str]]:
        """
        Momentum Layer (20%): RSI, MACD, ADX
        """
        score = 0
        reasons = []
        
        rsi = market_data.get('rsi', 50)
        macd = market_data.get('macd', 0)
        macd_signal = market_data.get('macd_signal', 0)
        adx = market_data.get('adx', 0)
        
        # RSI Analysis
        if rsi < 30:
            score += 30
            reasons.append("RSI Oversold")
        elif rsi > 70:
            score += 30
            reasons.append("RSI Overbought")
        
        # MACD Crossover
        if macd > macd_signal:
            score += 35
            reasons.append("MACD Bullish Crossover")
        elif macd < macd_signal:
            score += 35
            reasons.append("MACD Bearish Crossover")
        
        # ADX Strength
        if adx > 25:
            score += 35
            reasons.append(f"Strong Trend (ADX: {adx:.2f})")
        
        return min(score, 100), reasons
    
    def _analyze_smart_money(self, market_data: Dict) -> Tuple[float, List[str]]:
        """
        Smart Money Layer (20%): Liquidity sweeps and Order Blocks
        """
        score = 0
        reasons = []
        
        liquidity_sweep = market_data.get('liquidity_sweep', False)
        order_block = market_data.get('order_block', False)
        volume_spike = market_data.get('volume_spike', False)
        
        if liquidity_sweep:
            score += 40
            reasons.append("Liquidity Sweep Detected")
        
        if order_block:
            score += 40
            reasons.append("Order Block Identified")
        
        if volume_spike:
            score += 20
            reasons.append("Institutional Volume Spike")
        
        return min(score, 100), reasons
    
    def _analyze_market_state(self, market_data: Dict) -> Tuple[float, List[str]]:
        """
        Market State Layer (15%): ATR volatility and session timing
        """
        score = 0
        reasons = []
        
        atr = market_data.get('atr', 0)
        atr_threshold = market_data.get('atr_threshold', 100)
        session = market_data.get('session', 'UNKNOWN')
        
        # Volatility Filter
        if atr < atr_threshold:
            score += 50
            reasons.append(f"Normal Volatility (ATR: {atr:.2f})")
        
        # Session Timing
        if session in ['London', 'NewYork']:
            score += 50
            reasons.append(f"Optimal Session: {session}")
        
        return min(score, 100), reasons
    
    def _determine_action(self, market_data: Dict, probability: float) -> SignalAction:
        """Determine if signal is BUY or SELL"""
        trend = market_data.get('trend', 'NEUTRAL')
        
        if trend == 'BULLISH' and probability > self.min_score_threshold:
            return SignalAction.BUY
        elif trend == 'BEARISH' and probability > self.min_score_threshold:
            return SignalAction.SELL
        
        return SignalAction.NEUTRAL
    
    def _calculate_strength_level(self, probability: float) -> str:
        """Categorize signal strength"""
        if probability >= 90:
            return "Institutional"
        elif probability >= 80:
            return "Strong"
        elif probability >= 75:
            return "Moderate"
        else:
            return "Weak"
    
    def _calculate_stop_loss(self, market_data: Dict, action: SignalAction) -> float:
        """Calculate stop loss based on recent swing low/high"""
        if action == SignalAction.BUY:
            return market_data.get('swing_low', 0)
        else:
            return market_data.get('swing_high', 0)
    
    def _calculate_take_profit(self, market_data: Dict, action: SignalAction) -> float:
        """Calculate take profit using 1:2 or 1:3 risk-reward ratio"""
        entry = market_data.get('current_price', 0)
        
        if action == SignalAction.BUY:
            sl = market_data.get('swing_low', 0)
            risk = entry - sl
            return entry + (risk * 2)  # 1:2 ratio
        else:
            sl = market_data.get('swing_high', 0)
            risk = sl - entry
            return entry - (risk * 2)  # 1:2 ratio
