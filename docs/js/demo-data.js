/**
 * Demo Data for Rinse Repeat Labs Static Demo
 * All data is fictional and for demonstration purposes only.
 */

const DemoData = {
    // Sample Ideas
    ideas: [
        {
            id: "idea-001",
            name: "FitTrack Pro",
            description: "A comprehensive fitness tracking app with AI-powered workout recommendations and meal planning.",
            submitter_name: "Demo User",
            submitter_email: "demo@example.com",
            platforms: ["iOS", "Android"],
            revenue_model: "subscription",
            status: "approved",
            created_at: "Jan 15, 2026"
        },
        {
            id: "idea-002",
            name: "PetPal Connect",
            description: "Social network for pet owners with vet appointment scheduling and pet health tracking.",
            submitter_name: "Demo User",
            submitter_email: "demo@example.com",
            platforms: ["iOS", "Android", "Web"],
            revenue_model: "freemium",
            status: "in_development",
            created_at: "Jan 12, 2026"
        },
        {
            id: "idea-003",
            name: "StudyBuddy AI",
            description: "AI tutoring app that adapts to student learning styles with practice quizzes and progress tracking.",
            submitter_name: "Demo User",
            submitter_email: "demo@example.com",
            platforms: ["iOS", "Android", "Web"],
            revenue_model: "subscription",
            status: "submitted",
            created_at: "Jan 20, 2026"
        },
        {
            id: "idea-004",
            name: "GreenThumb Garden",
            description: "Plant care reminder app with species identification and community gardening tips.",
            submitter_name: "Demo User",
            submitter_email: "demo@example.com",
            platforms: ["iOS", "Android"],
            revenue_model: "one_time",
            status: "under_review",
            created_at: "Jan 18, 2026"
        },
        {
            id: "idea-005",
            name: "BudgetWise",
            description: "Personal finance app with expense categorization and savings goal tracking.",
            submitter_name: "Demo User",
            submitter_email: "demo@example.com",
            platforms: ["iOS", "Android", "Web"],
            revenue_model: "freemium",
            status: "submitted",
            created_at: "Jan 22, 2026"
        }
    ],

    // Sample Testers
    testers: [
        {
            id: "tester-001",
            name: "Alex Johnson",
            email: "alex.j@example.com",
            devices: ["iPhone 15", "iPad Pro"],
            status: "active",
            location: "San Francisco, CA",
            joined_at: "Dec 1, 2025"
        },
        {
            id: "tester-002",
            name: "Sam Rivera",
            email: "sam.r@example.com",
            devices: ["Pixel 8", "Samsung Galaxy Tab"],
            status: "active",
            location: "Austin, TX",
            joined_at: "Dec 5, 2025"
        },
        {
            id: "tester-003",
            name: "Jordan Lee",
            email: "jordan.l@example.com",
            devices: ["iPhone 14", "MacBook Air"],
            status: "active",
            location: "Seattle, WA",
            joined_at: "Dec 10, 2025"
        },
        {
            id: "tester-004",
            name: "Casey Morgan",
            email: "casey.m@example.com",
            devices: ["Samsung Galaxy S24"],
            status: "pending",
            location: "Denver, CO",
            joined_at: "Jan 15, 2026"
        },
        {
            id: "tester-005",
            name: "Taylor Kim",
            email: "taylor.k@example.com",
            devices: ["iPhone 15 Pro", "iPad Mini"],
            status: "active",
            location: "Portland, OR",
            joined_at: "Dec 20, 2025"
        }
    ],

    // Sample Clients
    clients: [
        {
            id: "client-001",
            name: "TechStart Inc.",
            contact_name: "Maria Garcia",
            email: "maria@techstart.example.com",
            status: "active",
            projects_count: 2,
            total_revenue: 45000
        },
        {
            id: "client-002",
            name: "FitLife Co.",
            contact_name: "David Chen",
            email: "david@fitlife.example.com",
            status: "active",
            projects_count: 1,
            total_revenue: 28000
        },
        {
            id: "client-003",
            name: "EduTech Solutions",
            contact_name: "Sarah Williams",
            email: "sarah@edutech.example.com",
            status: "active",
            projects_count: 1,
            total_revenue: 35000
        },
        {
            id: "client-004",
            name: "GreenWorld Apps",
            contact_name: "Michael Brown",
            email: "michael@greenworld.example.com",
            status: "prospect",
            projects_count: 0,
            total_revenue: 0
        },
        {
            id: "client-005",
            name: "HealthFirst Digital",
            contact_name: "Emily Davis",
            email: "emily@healthfirst.example.com",
            status: "active",
            projects_count: 1,
            total_revenue: 52000
        }
    ],

    // Sample Projects
    projects: [
        {
            id: "proj-001",
            name: "FitTrack Pro App",
            client_id: "client-002",
            client_name: "FitLife Co.",
            status: "development",
            tech_stack: ["React Native", "Node.js", "PostgreSQL"],
            start_date: "Nov 1, 2025",
            target_date: "Mar 15, 2026",
            contract_value: 28000
        },
        {
            id: "proj-002",
            name: "TechStart Dashboard",
            client_id: "client-001",
            client_name: "TechStart Inc.",
            status: "active",
            tech_stack: ["React", "Python", "MongoDB"],
            start_date: "Oct 15, 2025",
            target_date: "Feb 28, 2026",
            contract_value: 32000
        },
        {
            id: "proj-003",
            name: "StudyBuddy MVP",
            client_id: "client-003",
            client_name: "EduTech Solutions",
            status: "planning",
            tech_stack: ["Flutter", "Firebase", "OpenAI API"],
            start_date: "Feb 1, 2026",
            target_date: "May 30, 2026",
            contract_value: 35000
        },
        {
            id: "proj-004",
            name: "HealthFirst Patient Portal",
            client_id: "client-005",
            client_name: "HealthFirst Digital",
            status: "testing",
            tech_stack: ["Vue.js", "Django", "PostgreSQL"],
            start_date: "Sep 1, 2025",
            target_date: "Jan 31, 2026",
            contract_value: 52000
        }
    ],

    // Sample Finances
    finances: {
        total_revenue: 160000,
        outstanding: 24500,
        expenses: 45000,
        invoices: [
            {
                id: "inv-001",
                client_name: "TechStart Inc.",
                amount: 16000,
                status: "paid",
                date: "Jan 1, 2026"
            },
            {
                id: "inv-002",
                client_name: "FitLife Co.",
                amount: 14000,
                status: "sent",
                date: "Jan 15, 2026"
            },
            {
                id: "inv-003",
                client_name: "HealthFirst Digital",
                amount: 10500,
                status: "paid",
                date: "Dec 15, 2025"
            }
        ]
    },

    // Agent Information
    agents: {
        ceo: {
            id: "ceo",
            name: "Chief Executive Officer",
            short_name: "CEO",
            team: "Executive",
            description: "Provides strategic vision and leadership for the company. Makes high-level decisions about company direction and priorities.",
            color: "#ffd700"
        },
        cfo: {
            id: "cfo",
            name: "Chief Financial Officer",
            short_name: "CFO",
            team: "Executive",
            description: "Manages financial planning, risk management, and financial reporting. Advises on pricing and profitability.",
            color: "#28a745"
        },
        cito: {
            id: "cito",
            name: "Chief Information Technology Officer",
            short_name: "CITO",
            team: "Executive",
            description: "Oversees technology strategy and infrastructure. Evaluates technical feasibility of projects.",
            color: "#17a2b8"
        },
        sales: {
            id: "sales",
            name: "Sales Director",
            short_name: "Sales",
            team: "Executive",
            description: "Drives revenue growth and manages client relationships. Identifies new business opportunities.",
            color: "#fd7e14"
        },
        legal: {
            id: "legal",
            name: "Legal Counsel",
            short_name: "Legal",
            team: "Executive",
            description: "Provides legal guidance on contracts, compliance, and intellectual property matters.",
            color: "#6c757d"
        },
        dev_lead: {
            id: "dev_lead",
            name: "Development Lead",
            short_name: "Dev Lead",
            team: "Technical",
            description: "Leads software development efforts. Makes architectural decisions and ensures code quality.",
            color: "#007bff"
        },
        design_lead: {
            id: "design_lead",
            name: "Design Lead",
            short_name: "Design Lead",
            team: "Technical",
            description: "Leads UI/UX design. Creates user-centered designs and maintains design system consistency.",
            color: "#e83e8c"
        },
        qa_lead: {
            id: "qa_lead",
            name: "Quality Assurance Lead",
            short_name: "QA Lead",
            team: "Technical",
            description: "Ensures software quality through testing strategies. Manages bug tracking and release quality.",
            color: "#6f42c1"
        },
        pm: {
            id: "pm",
            name: "Project Manager",
            short_name: "PM",
            team: "Operations",
            description: "Coordinates project timelines and resources. Ensures projects stay on track and stakeholders are aligned.",
            color: "#20c997"
        },
        customer_success: {
            id: "customer_success",
            name: "Customer Success Manager",
            short_name: "Customer Success",
            team: "Operations",
            description: "Ensures client satisfaction and retention. Manages onboarding and ongoing client relationships.",
            color: "#f8b500"
        },
        marketing: {
            id: "marketing",
            name: "Marketing Director",
            short_name: "Marketing",
            team: "Operations",
            description: "Develops marketing strategies and brand positioning. Manages content and lead generation.",
            color: "#ff6b6b"
        },
        support: {
            id: "support",
            name: "Support Lead",
            short_name: "Support",
            team: "Operations",
            description: "Manages customer support operations. Ensures timely resolution of issues and feedback collection.",
            color: "#4ecdc4"
        }
    }
};

// Mock AI Responses for different agents
const MockResponses = {
    ceo: [
        "From a strategic perspective, this initiative aligns well with our company vision. I recommend we proceed with a phased approach to minimize risk while maximizing learning opportunities.",
        "This is an exciting opportunity. Let's ensure we have proper resource allocation and clear success metrics before moving forward. I'd like to see a brief proposal from the relevant teams.",
        "I appreciate the thorough analysis. My recommendation is to prioritize customer value while keeping an eye on sustainable growth. Let's schedule a follow-up to discuss implementation timeline."
    ],
    cfo: [
        "Looking at the financial implications, this project has a healthy ROI potential. I recommend we structure the pricing to ensure profitability while remaining competitive in the market.",
        "Based on our current cash flow projections, we can accommodate this investment. However, I suggest we establish clear milestones tied to budget releases to maintain financial discipline.",
        "The numbers look promising. I'd recommend a 70/30 payment structure with the client to balance cash flow needs with project delivery risk."
    ],
    cito: [
        "From a technical standpoint, I recommend using a modern tech stack that balances development speed with long-term maintainability. React Native for mobile would give us cross-platform efficiency.",
        "The proposed architecture is solid. I'd suggest adding a caching layer to improve performance and considering serverless functions for better scalability.",
        "This is technically feasible within our timeline. I recommend we conduct a brief technical spike to validate our assumptions before committing to the full implementation."
    ],
    dev_lead: [
        "I can have the development team start on this next sprint. We'll use our standard agile methodology with two-week iterations. Expect the MVP in approximately 6-8 weeks.",
        "The technical requirements are clear. I'll break this down into user stories and work with the team to estimate effort. We should plan for code reviews and automated testing throughout.",
        "This is a well-scoped feature request. I recommend we implement it using our existing component library to ensure consistency and speed up development."
    ],
    design_lead: [
        "I'll create wireframes and a design prototype for user testing before we move to development. This will help validate our UX assumptions early in the process.",
        "The user experience should prioritize simplicity and accessibility. I recommend following our established design system while incorporating mobile-first responsive patterns.",
        "I've reviewed the requirements and have some ideas for improving the user flow. Let me put together some concepts for review by end of week."
    ],
    qa_lead: [
        "I'll develop a comprehensive test plan covering unit tests, integration tests, and end-to-end user scenarios. We should aim for 80% code coverage minimum.",
        "Based on the feature scope, I recommend both automated testing and a manual QA pass before release. I'll coordinate with the testers for beta feedback as well.",
        "Quality gates will be in place at each milestone. I'll work with Dev Lead to ensure we have proper CI/CD pipelines for continuous quality validation."
    ],
    pm: [
        "I'll create a detailed project timeline with clear milestones and dependencies. We'll use our standard project management tools for tracking and stakeholder communication.",
        "Based on team capacity and project requirements, I estimate this will take 8-10 weeks. I'll schedule weekly check-ins to ensure we stay on track.",
        "I'll coordinate with all teams to ensure alignment on priorities and timelines. Risk management and contingency planning will be built into our project plan."
    ],
    sales: [
        "This solution addresses a clear market need. I can see strong potential for both new client acquisition and upselling to existing accounts.",
        "I've been getting positive signals from prospects about this type of feature. Let me put together a go-to-market strategy to capitalize on the opportunity.",
        "Pricing should reflect the value delivered to clients. I recommend we position this as a premium offering with clear ROI messaging."
    ],
    legal: [
        "I'll review the contract terms to ensure we have appropriate IP protections and liability limitations. Standard NDAs should be in place before sharing proprietary information.",
        "From a compliance perspective, we need to ensure GDPR and data privacy requirements are addressed. I'll provide guidelines for the development team.",
        "The agreement structure looks reasonable. I recommend adding a clear change order process and dispute resolution clause."
    ],
    marketing: [
        "This launch presents a great storytelling opportunity. I'll develop a content strategy including blog posts, case studies, and social media campaigns.",
        "Our target audience will respond well to messaging focused on efficiency and innovation. I recommend a multi-channel approach with emphasis on LinkedIn and industry publications.",
        "I'll work with Design Lead on visual assets and with Sales on lead nurturing materials. We should plan for a soft launch followed by a broader announcement."
    ],
    customer_success: [
        "I'll develop an onboarding program to ensure smooth client adoption. This includes training materials, documentation, and regular check-in schedules.",
        "Client feedback has been positive so far. I'll continue to gather insights and share them with the product team for continuous improvement.",
        "Retention strategies should focus on demonstrating ongoing value. I recommend quarterly business reviews and proactive feature education."
    ],
    support: [
        "I'll prepare the support team with knowledge base articles and troubleshooting guides. We'll be ready to handle inquiries from day one of launch.",
        "Current support metrics are healthy. Average response time is under 2 hours and satisfaction ratings are at 4.7/5 stars.",
        "I recommend establishing clear escalation paths and SLA commitments. The team is trained and ready to provide excellent support."
    ]
};

// Function to get a random mock response for an agent
function getMockResponse(agentId) {
    const responses = MockResponses[agentId];
    if (responses && responses.length > 0) {
        return responses[Math.floor(Math.random() * responses.length)];
    }
    return "Thank you for the question. Let me analyze this from my area of expertise and provide thoughtful recommendations.";
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DemoData, MockResponses, getMockResponse };
}
