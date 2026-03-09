'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { Trophy, TrendingUp, Award, BookOpen, Users, DollarSign, Star, ChevronRight } from 'lucide-react';

interface University {
  id: number;
  name: string;
  location: string;
  grade: string;
  score: number;
  framework: 'NAAC' | 'NBA';
  rank: number;
  logo: string;
  achievements: string[];
  keyMetrics: {
    researchProjects: number;
    fundingAmount: string;
    facultyCount: number;
    studentRatio: string;
  };
  successFactors: string[];
}

const topUniversities: University[] = [
  {
    id: 1,
    name: "Indian Institute of Technology, Bombay",
    location: "Mumbai, Maharashtra",
    grade: "A++",
    score: 98.5,
    framework: "NAAC",
    rank: 1,
    logo: "🏛️",
    achievements: [
      "Highest research output in India",
      "150+ international collaborations",
      "₹500+ Crore annual research funding"
    ],
    keyMetrics: {
      researchProjects: 450,
      fundingAmount: "₹520 Cr",
      facultyCount: 680,
      studentRatio: "1:8"
    },
    successFactors: [
      "Comprehensive documentation with detailed data tables",
      "Strong industry partnerships and funding sources",
      "Extensive research publications and patents",
      "Regular faculty development programs",
      "State-of-the-art infrastructure and labs"
    ]
  },
  {
    id: 2,
    name: "Indian Institute of Science, Bangalore",
    location: "Bangalore, Karnataka",
    grade: "A++",
    score: 97.8,
    framework: "NAAC",
    rank: 2,
    logo: "🔬",
    achievements: [
      "Top research institution in Asia",
      "200+ PhD scholars annually",
      "₹450+ Crore research grants"
    ],
    keyMetrics: {
      researchProjects: 380,
      fundingAmount: "₹465 Cr",
      facultyCount: 520,
      studentRatio: "1:6"
    },
    successFactors: [
      "Focus on cutting-edge research and innovation",
      "Strong international faculty exchange programs",
      "Detailed evidence of research impact",
      "Comprehensive student support systems",
      "Excellence in interdisciplinary research"
    ]
  },
  {
    id: 3,
    name: "Jawaharlal Nehru University",
    location: "New Delhi",
    grade: "A++",
    score: 96.2,
    framework: "NAAC",
    rank: 3,
    logo: "📚",
    achievements: [
      "Excellence in social sciences",
      "100+ international MoUs",
      "₹280+ Crore annual funding"
    ],
    keyMetrics: {
      researchProjects: 320,
      fundingAmount: "₹285 Cr",
      facultyCount: 580,
      studentRatio: "1:10"
    },
    successFactors: [
      "Strong emphasis on research methodology",
      "Comprehensive documentation practices",
      "Active student research participation",
      "Regular quality audits and improvements",
      "Diverse funding sources documented"
    ]
  },
  {
    id: 4,
    name: "University of Delhi",
    location: "New Delhi",
    grade: "A++",
    score: 95.8,
    framework: "NAAC",
    rank: 4,
    logo: "🎯",
    achievements: [
      "Largest university system in India",
      "90+ affiliated colleges",
      "₹350+ Crore research funding"
    ],
    keyMetrics: {
      researchProjects: 410,
      fundingAmount: "₹365 Cr",
      facultyCount: 720,
      studentRatio: "1:14"
    },
    successFactors: [
      "Extensive network of research centers",
      "Strong documentation of collaborative projects",
      "Regular quality enhancement initiatives",
      "Comprehensive student welfare programs",
      "Detailed evidence of community engagement"
    ]
  },
  {
    id: 5,
    name: "Banaras Hindu University",
    location: "Varanasi, Uttar Pradesh",
    grade: "A++",
    score: 95.2,
    framework: "NAAC",
    rank: 5,
    logo: "🕉️",
    achievements: [
      "Asia's largest residential university",
      "120+ departments",
      "₹320+ Crore annual funding"
    ],
    keyMetrics: {
      researchProjects: 390,
      fundingAmount: "₹335 Cr",
      facultyCount: 650,
      studentRatio: "1:12"
    },
    successFactors: [
      "Holistic education approach documented",
      "Strong cultural and academic integration",
      "Comprehensive infrastructure development records",
      "Active industry collaboration programs",
      "Detailed student outcome tracking"
    ]
  },
  {
    id: 6,
    name: "Indian Institute of Technology, Delhi",
    location: "New Delhi",
    grade: "A++",
    score: 94.9,
    framework: "NAAC",
    rank: 6,
    logo: "🏗️",
    achievements: [
      "Leading engineering institution",
      "140+ international partnerships",
      "₹480+ Crore research grants"
    ],
    keyMetrics: {
      researchProjects: 425,
      fundingAmount: "₹495 Cr",
      facultyCount: 590,
      studentRatio: "1:9"
    },
    successFactors: [
      "Excellence in technology transfer",
      "Strong startup incubation ecosystem",
      "Comprehensive patent documentation",
      "Regular industry-sponsored research",
      "Detailed innovation metrics tracking"
    ]
  },
  {
    id: 7,
    name: "Anna University",
    location: "Chennai, Tamil Nadu",
    grade: "A+",
    score: 94.3,
    framework: "NAAC",
    rank: 7,
    logo: "🌟",
    achievements: [
      "Top technical university in South India",
      "230+ affiliated colleges",
      "₹290+ Crore research funding"
    ],
    keyMetrics: {
      researchProjects: 350,
      fundingAmount: "₹305 Cr",
      facultyCount: 540,
      studentRatio: "1:13"
    },
    successFactors: [
      "Strong regional industry connections",
      "Comprehensive curriculum documentation",
      "Regular accreditation of affiliated colleges",
      "Detailed quality assurance mechanisms",
      "Active research publication tracking"
    ]
  },
  {
    id: 8,
    name: "National Institute of Technology, Trichy",
    location: "Tiruchirappalli, Tamil Nadu",
    grade: "A+",
    score: 94.5,
    framework: "NBA",
    rank: 1,
    logo: "⚙️",
    achievements: [
      "Top NBA accredited engineering college",
      "85% placement rate",
      "₹180+ Crore research funding"
    ],
    keyMetrics: {
      researchProjects: 280,
      fundingAmount: "₹185 Cr",
      facultyCount: 450,
      studentRatio: "1:12"
    },
    successFactors: [
      "Strong industry-academia collaboration",
      "Detailed outcome-based education documentation",
      "Regular curriculum updates aligned with industry",
      "Comprehensive student assessment records",
      "Active alumni engagement and feedback"
    ]
  },
  {
    id: 9,
    name: "Birla Institute of Technology and Science, Pilani",
    location: "Pilani, Rajasthan",
    grade: "A+",
    score: 93.8,
    framework: "NBA",
    rank: 2,
    logo: "🎓",
    achievements: [
      "Premier private technical institution",
      "90+ industry partnerships",
      "₹150+ Crore research grants"
    ],
    keyMetrics: {
      researchProjects: 240,
      fundingAmount: "₹155 Cr",
      facultyCount: 420,
      studentRatio: "1:15"
    },
    successFactors: [
      "Innovative teaching methodologies documented",
      "Strong focus on practical learning outcomes",
      "Comprehensive quality assurance systems",
      "Regular stakeholder feedback integration",
      "Detailed program outcome assessments"
    ]
  },
  {
    id: 10,
    name: "National Institute of Technology, Karnataka",
    location: "Surathkal, Karnataka",
    grade: "A+",
    score: 93.2,
    framework: "NBA",
    rank: 3,
    logo: "🌊",
    achievements: [
      "Coastal engineering excellence",
      "80+ industry collaborations",
      "₹165+ Crore research funding"
    ],
    keyMetrics: {
      researchProjects: 260,
      fundingAmount: "₹172 Cr",
      facultyCount: 430,
      studentRatio: "1:13"
    },
    successFactors: [
      "Strong focus on applied research",
      "Comprehensive lab infrastructure documentation",
      "Regular industry feedback integration",
      "Detailed student project tracking",
      "Active participation in national competitions"
    ]
  },
  {
    id: 11,
    name: "Vellore Institute of Technology",
    location: "Vellore, Tamil Nadu",
    grade: "A+",
    score: 92.8,
    framework: "NBA",
    rank: 4,
    logo: "💡",
    achievements: [
      "Leading private university",
      "100+ international tie-ups",
      "₹140+ Crore research grants"
    ],
    keyMetrics: {
      researchProjects: 230,
      fundingAmount: "₹148 Cr",
      facultyCount: 480,
      studentRatio: "1:16"
    },
    successFactors: [
      "Strong international collaboration programs",
      "Comprehensive student exchange documentation",
      "Regular curriculum innovation",
      "Detailed placement records and tracking",
      "Active entrepreneurship development"
    ]
  },
  {
    id: 12,
    name: "Manipal Academy of Higher Education",
    location: "Manipal, Karnataka",
    grade: "A+",
    score: 92.3,
    framework: "NAAC",
    rank: 8,
    logo: "🏥",
    achievements: [
      "Excellence in medical education",
      "85+ international partnerships",
      "₹220+ Crore research funding"
    ],
    keyMetrics: {
      researchProjects: 310,
      fundingAmount: "₹235 Cr",
      facultyCount: 560,
      studentRatio: "1:11"
    },
    successFactors: [
      "Strong healthcare research documentation",
      "Comprehensive clinical training records",
      "Regular international accreditation",
      "Detailed patient care outcome tracking",
      "Active community health programs"
    ]
  },
  {
    id: 13,
    name: "Jadavpur University",
    location: "Kolkata, West Bengal",
    grade: "A+",
    score: 91.9,
    framework: "NAAC",
    rank: 9,
    logo: "📖",
    achievements: [
      "Excellence in arts and sciences",
      "70+ research centers",
      "₹195+ Crore annual funding"
    ],
    keyMetrics: {
      researchProjects: 285,
      fundingAmount: "₹208 Cr",
      facultyCount: 490,
      studentRatio: "1:14"
    },
    successFactors: [
      "Strong interdisciplinary research culture",
      "Comprehensive publication tracking",
      "Regular quality enhancement cells",
      "Detailed student mentorship programs",
      "Active social outreach documentation"
    ]
  },
  {
    id: 14,
    name: "Amrita Vishwa Vidyapeetham",
    location: "Coimbatore, Tamil Nadu",
    grade: "A+",
    score: 91.5,
    framework: "NAAC",
    rank: 10,
    logo: "🙏",
    achievements: [
      "Fastest growing private university",
      "95+ international collaborations",
      "₹180+ Crore research grants"
    ],
    keyMetrics: {
      researchProjects: 270,
      fundingAmount: "₹192 Cr",
      facultyCount: 510,
      studentRatio: "1:15"
    },
    successFactors: [
      "Strong value-based education documentation",
      "Comprehensive social service integration",
      "Regular innovation and patent filing",
      "Detailed sustainability initiatives",
      "Active disaster management research"
    ]
  },
  {
    id: 15,
    name: "Indian Institute of Technology, Madras",
    location: "Chennai, Tamil Nadu",
    grade: "A++",
    score: 98.2,
    framework: "NAAC",
    rank: 11,
    logo: "🚀",
    achievements: [
      "Top ranked IIT in India",
      "160+ international partnerships",
      "₹510+ Crore research funding"
    ],
    keyMetrics: {
      researchProjects: 440,
      fundingAmount: "₹528 Cr",
      facultyCount: 620,
      studentRatio: "1:7"
    },
    successFactors: [
      "Excellence in aerospace and automotive research",
      "Strong startup ecosystem documentation",
      "Comprehensive industry-sponsored projects",
      "Regular international faculty exchange",
      "Detailed innovation and IP management"
    ]
  }
];

export default function TopUniversitiesPage() {
  const [selectedFramework, setSelectedFramework] = useState<'ALL' | 'NAAC' | 'NBA'>('ALL');
  const [selectedUniversity, setSelectedUniversity] = useState<University | null>(null);

  const filteredUniversities = selectedFramework === 'ALL' 
    ? topUniversities 
    : topUniversities.filter(u => u.framework === selectedFramework);

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 p-8 ml-64">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Trophy className="text-yellow-500" size={32} />
            <h1 className="text-3xl font-bold text-foreground">Top Ranked Universities</h1>
          </div>
          <p className="text-muted-foreground">
            Learn from the best - Explore what top-ranked institutions did to achieve excellence
          </p>
        </div>

        {/* Framework Filter */}
        <div className="flex gap-4 mb-6">
          {['ALL', 'NAAC', 'NBA'].map((framework) => (
            <button
              key={framework}
              onClick={() => setSelectedFramework(framework as any)}
              className={`px-6 py-2 rounded-lg font-medium transition ${
                selectedFramework === framework
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                  : 'bg-slate-800/50 text-muted-foreground hover:bg-slate-700/50'
              }`}
            >
              {framework}
            </button>
          ))}
        </div>

        {/* Universities Grid */}
        <div className="grid grid-cols-1 gap-6">
          {filteredUniversities.map((university) => (
            <div
              key={university.id}
              className="glass-card p-6 border border-border/50 rounded-xl hover:border-cyan-500/50 transition cursor-pointer"
              onClick={() => setSelectedUniversity(university)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-4">
                  <div className="text-5xl">{university.logo}</div>
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-xl font-bold text-foreground">{university.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                        university.grade === 'A++' ? 'bg-yellow-500/20 text-yellow-400' :
                        university.grade === 'A+' ? 'bg-green-500/20 text-green-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {university.grade}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{university.location}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="flex items-center gap-1 text-cyan-400">
                        <Award size={16} />
                        Rank #{university.rank} ({university.framework})
                      </span>
                      <span className="flex items-center gap-1 text-purple-400">
                        <Star size={16} />
                        Score: {university.score}%
                      </span>
                    </div>
                  </div>
                </div>
                <ChevronRight className="text-muted-foreground" size={24} />
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-slate-800/30 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <BookOpen size={16} className="text-cyan-400" />
                    <span className="text-xs text-muted-foreground">Projects</span>
                  </div>
                  <p className="text-lg font-bold text-foreground">{university.keyMetrics.researchProjects}</p>
                </div>
                <div className="bg-slate-800/30 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <DollarSign size={16} className="text-green-400" />
                    <span className="text-xs text-muted-foreground">Funding</span>
                  </div>
                  <p className="text-lg font-bold text-foreground">{university.keyMetrics.fundingAmount}</p>
                </div>
                <div className="bg-slate-800/30 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <Users size={16} className="text-purple-400" />
                    <span className="text-xs text-muted-foreground">Faculty</span>
                  </div>
                  <p className="text-lg font-bold text-foreground">{university.keyMetrics.facultyCount}</p>
                </div>
                <div className="bg-slate-800/30 p-3 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp size={16} className="text-yellow-400" />
                    <span className="text-xs text-muted-foreground">Ratio</span>
                  </div>
                  <p className="text-lg font-bold text-foreground">{university.keyMetrics.studentRatio}</p>
                </div>
              </div>

              {/* Achievements */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-foreground mb-2">Key Achievements:</h4>
                <div className="flex flex-wrap gap-2">
                  {university.achievements.map((achievement, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-cyan-500/10 text-cyan-400 rounded-full text-xs"
                    >
                      {achievement}
                    </span>
                  ))}
                </div>
              </div>

              {/* Success Factors Preview */}
              <div>
                <h4 className="text-sm font-semibold text-foreground mb-2">Success Factors:</h4>
                <ul className="space-y-1">
                  {university.successFactors.slice(0, 3).map((factor, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-green-400 mt-1">✓</span>
                      {factor}
                    </li>
                  ))}
                </ul>
                <button className="text-sm text-cyan-400 hover:text-cyan-300 mt-2 flex items-center gap-1">
                  View all success factors <ChevronRight size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Detailed Modal */}
        {selectedUniversity && (
          <div
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8"
            onClick={() => setSelectedUniversity(null)}
          >
            <div
              className="glass-card border border-border/50 rounded-2xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-start gap-4">
                  <div className="text-6xl">{selectedUniversity.logo}</div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground mb-1">{selectedUniversity.name}</h2>
                    <p className="text-muted-foreground">{selectedUniversity.location}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedUniversity(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-foreground mb-3">Complete Success Strategy</h3>
                  <ul className="space-y-3">
                    {selectedUniversity.successFactors.map((factor, idx) => (
                      <li key={idx} className="flex items-start gap-3 p-3 bg-slate-800/30 rounded-lg">
                        <span className="text-green-400 font-bold">{idx + 1}.</span>
                        <span className="text-foreground">{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-foreground mb-3">How to Apply This to Your Institution</h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
                      <h4 className="font-semibold text-cyan-400 mb-2">Documentation</h4>
                      <p className="text-sm text-foreground">
                        Maintain detailed records of all activities with specific numbers, dates, and outcomes. 
                        Use data tables instead of narrative descriptions.
                      </p>
                    </div>
                    <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                      <h4 className="font-semibold text-purple-400 mb-2">Evidence Quality</h4>
                      <p className="text-sm text-foreground">
                        Include supporting documents like funding letters, project reports, and collaboration agreements. 
                        Ensure all claims are backed by verifiable evidence.
                      </p>
                    </div>
                    <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                      <h4 className="font-semibold text-green-400 mb-2">Continuous Improvement</h4>
                      <p className="text-sm text-foreground">
                        Regular internal audits, stakeholder feedback, and quality enhancement initiatives. 
                        Document all improvement actions taken.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
