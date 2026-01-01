

window.generatePDF = (data) => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();

    // Header
    doc.setFillColor(30, 41, 59); // Slate 900
    doc.rect(0, 0, pageWidth, 40, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(22);
    doc.setFont("helvetica", "bold");
    doc.text("All India Entrance Roadmap", 14, 20);
    
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.text(`Master Syllabus: ${data.master.name}`, 14, 30);

    // Body
    let y = 50;
    doc.setTextColor(0, 0, 0);

    // Master Syllabus Section
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Core Syllabus (Strict NCERT/Standard)", 14, y);
    y += 10;

    const subjects = data.master.syllabus || {};
    Object.keys(subjects).forEach(subject => {
        doc.setFontSize(14);
        doc.setTextColor(59, 130, 246); // Blue
        doc.text(subject, 14, y);
        y += 8;

        doc.setFontSize(10);
        doc.setTextColor(60, 60, 60);
        const topics = subjects[subject]; // Array of chapters/topics
        
        // Wrap text logic would go here, simplified for list
        doc.text(topics.join(", "), 14, y, { maxWidth: 180 });
        
        // Estimate height based on text length
        const lines = doc.splitTextToSize(topics.join(", "), 180);
        y += (lines.length * 5) + 5;
    });

    y += 10;

    // Satellite Exams Section
    if (data.satellites && data.satellites.length > 0) {
        doc.setFontSize(16);
        doc.setTextColor(0, 0, 0);
        doc.setFont("helvetica", "bold");
        doc.text("Exam Deviations (Other Entrance Exams)", 14, y);
        y += 10;

        data.satellites.forEach(sat => {
            doc.setFontSize(12);
            doc.setTextColor(147, 51, 234); // Purple
            doc.text(`${sat.name}`, 14, y);
            y += 6;
            
            doc.setFontSize(10);
            doc.setTextColor(80, 80, 80);
            doc.text(`Deviation: ${sat.deviation}`, 14, y, { maxWidth: 180 });
            y += 15;
        });
    }

    doc.save(`${data.master.name}_Syllabus.pdf`);
};
