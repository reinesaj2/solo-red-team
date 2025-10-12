#!/usr/bin/env python3
"""
Attack Analytics Visualization for CS 660 Strategic Password Tester
Creates matplotlib charts analyzing attack patterns, timing, and success rates
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone
import json
import numpy as np
from pathlib import Path

class AttackAnalyzer:
    def __init__(self, csv_file: str, stats_file: str):
        self.csv_file = csv_file
        self.stats_file = stats_file
        self.df = None
        self.stats = None
        
        # Set up visualization style
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def load_data(self):
        """Load attack results and session statistics"""
        try:
            # Load CSV data
            if Path(self.csv_file).exists():
                self.df = pd.read_csv(self.csv_file)
                self.df['timestamp'] = pd.to_datetime(self.df['ts_utc'])
                print(f"Loaded {len(self.df)} attack attempts from {self.csv_file}")
            else:
                print(f"CSV file not found: {self.csv_file}")
                # Create dummy data for demonstration
                self.df = self._create_demo_data()
            
            # Load session statistics
            if Path(self.stats_file).exists():
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
                print(f"Loaded session statistics from {self.stats_file}")
            else:
                print(f"Stats file not found: {self.stats_file}")
                self.stats = self._create_demo_stats()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = self._create_demo_data()
            self.stats = self._create_demo_stats()
    
    def _create_demo_data(self):
        """Create demonstration data for visualization testing"""
        print("Creating demonstration data for visualization testing...")
        
        # Simulate realistic attack data
        now = datetime.now(timezone.utc)
        
        data = []
        targets = ['html_form', 'http_basic', 'http_digest']
        outcomes = ['failure', 'failure', 'failure', 'rate_limited', 'success']  # Weighted toward failures
        
        from datetime import timedelta
        for i in range(150):  # Simulate 150 attempts
            timestamp = now - timedelta(minutes=(150-i)//3, seconds=(i*2) % 60)
            target = targets[i % len(targets)]
            outcome = np.random.choice(outcomes, p=[0.8, 0.15, 0.03, 0.015, 0.005])  # Mostly failures
            
            data.append({
                'ts_utc': timestamp.isoformat(),
                'timestamp': timestamp,
                'target': target,
                'username': 'wangxx',
                'candidate_id': (i % 200) + 1,
                'http_status': 401 if outcome == 'failure' else (429 if outcome == 'rate_limited' else 200),
                'resp_ms': np.random.randint(200, 2000),
                'resp_hash': f'hash{i%10}',
                'outcome': outcome
            })
        
        return pd.DataFrame(data)
    
    def _create_demo_stats(self):
        """Create demonstration statistics"""
        return {
            'total_attempts': 150,
            'successful_logins': 1,
            'lockouts_detected': 2,
            'start_time': (datetime.now(timezone.utc).replace(hour=datetime.now().hour-1)).isoformat(),
            'end_time': datetime.now(timezone.utc).isoformat(),
            'duration_minutes': 63.5,
            'phase_transitions': [
                {'phase': 'A', 'start_time': '2025-09-10T12:00:00Z', 'description': 'Password spray top 30 candidates'},
                {'phase': 'B', 'start_time': '2025-09-10T12:20:00Z', 'description': 'Targeted attack up to 200 candidates per remaining user'}
            ]
        }
    
    def create_attempts_over_time_chart(self):
        """Create timeline chart of attack attempts"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Resample data to show attempts per minute
        df_resampled = self.df.set_index('timestamp').groupby([
            pd.Grouper(freq='1Min'), 'target'
        ]).size().reset_index(name='attempts')
        
        # Plot attempts by target
        for target in self.df['target'].unique():
            target_data = df_resampled[df_resampled['target'] == target]
            ax1.plot(target_data['timestamp'], target_data['attempts'], 
                    marker='o', label=target, linewidth=2, markersize=4)
        
        ax1.set_title('Attack Attempts Over Time by Target', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Attempts per Minute')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Cumulative attempts
        cumulative = self.df.set_index('timestamp').resample('1Min').size().cumsum()
        ax2.plot(cumulative.index, cumulative.values, color='red', linewidth=3)
        ax2.fill_between(cumulative.index, 0, cumulative.values, alpha=0.3, color='red')
        
        ax2.set_title('Cumulative Attack Attempts', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Total Attempts')
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax2.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig('/mnt/hgsf/cs660-p3-shared/evidence/attempts_over_time.png', dpi=300, bbox_inches='tight')
        print("Created: attempts_over_time.png")
        return fig
    
    def create_lockout_detection_chart(self):
        """Create chart showing lockout and rate limiting events"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Response time analysis (potential lockout indicator)
        response_times = self.df.groupby('target')['resp_ms'].describe()
        
        targets = response_times.index
        means = response_times['mean']
        maxs = response_times['max']
        
        x = np.arange(len(targets))
        width = 0.35
        
        ax1.bar(x - width/2, means, width, label='Mean Response Time', alpha=0.8)
        ax1.bar(x + width/2, maxs, width, label='Max Response Time', alpha=0.8)
        
        ax1.set_title('Response Time Analysis by Target', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Target')
        ax1.set_ylabel('Response Time (ms)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(targets, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Rate limiting and error analysis
        outcome_counts = self.df.groupby(['target', 'outcome']).size().unstack(fill_value=0)
        
        outcome_counts.plot(kind='bar', ax=ax2, stacked=True)
        ax2.set_title('Attack Outcomes by Target', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Target')
        ax2.set_ylabel('Number of Attempts')
        ax2.legend(title='Outcome')
        ax2.grid(True, alpha=0.3)
        
        # Rotate labels
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig('/mnt/hgsf/cs660-p3-shared/evidence/lockout_analysis.png', dpi=300, bbox_inches='tight')
        print("Created: lockout_analysis.png")
        return fig
    
    def create_success_rate_chart(self):
        """Create chart analyzing success rates by candidate rank"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Success rate by candidate ID (ranking)
        success_by_rank = self.df.groupby('candidate_id').agg({
            'outcome': lambda x: (x == 'success').sum(),
            'target': 'count'
        }).rename(columns={'outcome': 'successes', 'target': 'attempts'})
        
        success_by_rank['success_rate'] = success_by_rank['successes'] / success_by_rank['attempts'] * 100
        
        # Plot success rate for first 100 candidates
        top_candidates = success_by_rank.head(100)
        ax1.scatter(top_candidates.index, top_candidates['success_rate'], 
                   s=top_candidates['attempts']*10, alpha=0.6, c='green')
        ax1.set_title('Success Rate by Candidate Rank', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Candidate ID (Lower = Higher Priority)')
        ax1.set_ylabel('Success Rate (%)')
        ax1.grid(True, alpha=0.3)
        
        # Add annotation for bubble size
        ax1.text(0.7, 0.95, 'Bubble size = # attempts', transform=ax1.transAxes, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # HTTP status code distribution
        status_counts = self.df['http_status'].value_counts()
        colors = ['red' if status in [401, 403, 429] else 'green' if status == 200 else 'orange' 
                 for status in status_counts.index]
        
        ax2.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', 
               colors=colors, startangle=90)
        ax2.set_title('HTTP Status Code Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/mnt/hgsf/cs660-p3-shared/evidence/success_rate_analysis.png', dpi=300, bbox_inches='tight')
        print("Created: success_rate_analysis.png")
        return fig
    
    def create_comprehensive_dashboard(self):
        """Create comprehensive attack analytics dashboard"""
        fig = plt.figure(figsize=(20, 12))
        
        # Create subplot grid
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # 1. Attack timeline (top row, full width)
        ax1 = fig.add_subplot(gs[0, :])
        timeline_data = self.df.set_index('timestamp').resample('5Min').size()
        ax1.plot(timeline_data.index, timeline_data.values, marker='o', linewidth=2, markersize=4, color='blue')
        ax1.fill_between(timeline_data.index, 0, timeline_data.values, alpha=0.3, color='blue')
        ax1.set_title('Attack Timeline (5-minute intervals)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Attempts per 5 min')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # 2. Target distribution (middle left)
        ax2 = fig.add_subplot(gs[1, 0])
        target_counts = self.df['target'].value_counts()
        ax2.pie(target_counts.values, labels=target_counts.index, autopct='%1.1f%%', startangle=45)
        ax2.set_title('Attempts by Target', fontweight='bold')
        
        # 3. Outcome distribution (middle center-left)
        ax3 = fig.add_subplot(gs[1, 1])
        outcome_counts = self.df['outcome'].value_counts()
        colors = ['red' if outcome == 'failure' else 'green' if outcome == 'success' else 'orange' 
                 for outcome in outcome_counts.index]
        ax3.bar(outcome_counts.index, outcome_counts.values, color=colors)
        ax3.set_title('Attack Outcomes', fontweight='bold')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Response time distribution (middle center-right)
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.hist(self.df['resp_ms'], bins=30, alpha=0.7, color='purple')
        ax4.set_title('Response Time Distribution', fontweight='bold')
        ax4.set_xlabel('Response Time (ms)')
        ax4.set_ylabel('Frequency')
        
        # 5. Success rate heatmap (middle right)
        ax5 = fig.add_subplot(gs[1, 3])
        pivot_data = self.df.groupby(['target', 'outcome']).size().unstack(fill_value=0)
        if 'success' in pivot_data.columns and 'failure' in pivot_data.columns:
            success_rates = pivot_data['success'] / (pivot_data['success'] + pivot_data['failure']) * 100
            im = ax5.imshow(success_rates.values.reshape(-1, 1), cmap='RdYlGn', aspect='auto')
            ax5.set_yticks(range(len(success_rates)))
            ax5.set_yticklabels(success_rates.index)
            ax5.set_xticks([0])
            ax5.set_xticklabels(['Success Rate %'])
            # Add text annotations
            for i, rate in enumerate(success_rates.values):
                ax5.text(0, i, f'{rate:.1f}%', ha='center', va='center', fontweight='bold')
        ax5.set_title('Success Rate by Target', fontweight='bold')
        
        # 6. Phase analysis (bottom row)
        ax6 = fig.add_subplot(gs[2, :2])
        if self.stats and 'phase_transitions' in self.stats:
            phase_data = []
            for i, phase in enumerate(self.stats['phase_transitions']):
                phase_start = pd.to_datetime(phase['start_time'])
                if i < len(self.stats['phase_transitions']) - 1:
                    phase_end = pd.to_datetime(self.stats['phase_transitions'][i+1]['start_time'])
                else:
                    phase_end = self.df['timestamp'].max()
                
                phase_attempts = self.df[(self.df['timestamp'] >= phase_start) & 
                                       (self.df['timestamp'] < phase_end)]
                phase_data.append({
                    'phase': phase['phase'],
                    'attempts': len(phase_attempts),
                    'successes': len(phase_attempts[phase_attempts['outcome'] == 'success']),
                    'duration_min': (phase_end - phase_start).total_seconds() / 60
                })
            
            if phase_data:
                phase_df = pd.DataFrame(phase_data)
                x = np.arange(len(phase_df))
                width = 0.35
                
                ax6.bar(x - width/2, phase_df['attempts'], width, label='Total Attempts', alpha=0.8)
                ax6.bar(x + width/2, phase_df['successes'], width, label='Successes', alpha=0.8)
                ax6.set_title('Performance by Attack Phase', fontweight='bold')
                ax6.set_xlabel('Phase')
                ax6.set_ylabel('Count')
                ax6.set_xticks(x)
                ax6.set_xticklabels([f"Phase {p}" for p in phase_df['phase']])
                ax6.legend()
        
        # 7. Session statistics (bottom right)
        ax7 = fig.add_subplot(gs[2, 2:])
        if self.stats:
            stats_text = f"""
Session Statistics:
• Total Attempts: {self.stats.get('total_attempts', 'N/A')}
• Successful Logins: {self.stats.get('successful_logins', 'N/A')}
• Lockouts Detected: {self.stats.get('lockouts_detected', 'N/A')}
• Duration: {self.stats.get('duration_minutes', 'N/A'):.1f} minutes
• Success Rate: {(self.stats.get('successful_logins', 0) / max(self.stats.get('total_attempts', 1), 1) * 100):.2f}%
            """
            ax7.text(0.1, 0.5, stats_text.strip(), transform=ax7.transAxes, fontsize=12,
                    verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            ax7.set_title('Session Summary', fontweight='bold')
            ax7.axis('off')
        
        plt.suptitle('CS 660 Strategic Password Attack Analytics Dashboard', fontsize=16, fontweight='bold')
        plt.savefig('/mnt/hgsf/cs660-p3-shared/evidence/comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
        print("Created: comprehensive_dashboard.png")
        return fig
    
    def generate_all_charts(self):
        """Generate all visualization charts"""
        print("CS 660 Attack Analytics Visualization")
        print("=" * 40)
        
        self.load_data()
        
        print("\\nGenerating visualization charts...")
        
        # Generate individual charts
        self.create_attempts_over_time_chart()
        plt.close()
        
        self.create_lockout_detection_chart()
        plt.close()
        
        self.create_success_rate_chart()
        plt.close()
        
        # Generate comprehensive dashboard
        self.create_comprehensive_dashboard()
        plt.close()
        
        print("\\nAll charts generated successfully!")
        print("Charts saved to /mnt/hgsf/cs660-p3-shared/evidence/")


def main():
    """Main execution function"""
    analyzer = AttackAnalyzer(
        csv_file="/mnt/hgsf/cs660-p3-shared/logs/attack_results.csv",
        stats_file="/mnt/hgsf/cs660-p3-shared/evidence/session_statistics.json"
    )
    
    analyzer.generate_all_charts()
    
    print("\\nVisualization artifacts created:")
    print("  - attempts_over_time.png")
    print("  - lockout_analysis.png")
    print("  - success_rate_analysis.png")
    print("  - comprehensive_dashboard.png")


if __name__ == "__main__":
    main()