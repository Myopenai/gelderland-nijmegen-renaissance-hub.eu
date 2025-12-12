const fs = require('fs');
const path = require('path');

// Region data
const regions = [
    {
        name: 'Kleve',
        displayName: 'Kleve',
        regionLowercase: 'kleve',
        country: 'Germany',
        population: '52,000',
        area: '97.8',
        yearFounded: '1092',
        mayor: 'Wolfgang Gebing',
        website: 'www.kleve.de',
        randomFact: 'home to the beautiful Schwanenburg Castle and the famous botanical gardens, Forstgarten',
        keySectors: 'tourism, education, and healthcare',
        universities: 'Rhine-Waal University of Applied Sciences',
        sustainability: 'extensive cycling infrastructure and green energy initiatives'
    },
    {
        name: 'Emmerich',
        displayName: 'Emmerich am Rhein',
        regionLowercase: 'emmerich',
        country: 'Germany',
        population: '31,000',
        area: '80.11',
        yearFounded: '1233',
        mayor: 'Peter Hinze',
        website: 'www.emmerich.de',
        randomFact: 'famous for its Rhine Bridge, one of the most important border crossings between Germany and the Netherlands',
        keySectors: 'logistics, industry, and trade',
        universities: 'Lower Rhine University of Applied Sciences (nearby)',
        sustainability: 'riverfront redevelopment projects and flood protection measures'
    },
    {
        name: 'Arnhem',
        displayName: 'Arnhem',
        regionLowercase: 'arnhem',
        country: 'Netherlands',
        population: '162,000',
        area: '101.53',
        yearFounded: '893',
        mayor: 'Ahmed Marcouch',
        website: 'www.arnhem.nl',
        randomFact: 'known for the historic Battle of Arnhem during World War II and the famous Open Air Museum',
        keySectors: 'tourism, fashion, and sustainable energy',
        universities: 'HAN University of Applied Sciences, ArtEZ Institute of the Arts',
        sustainability: 'pioneer in sustainable urban development and electric transportation'
    },
    {
        name: 'Nijmegen',
        displayName: 'Nijmegen',
        regionLowercase: 'nijmegen',
        country: 'Netherlands',
        population: '177,000',
        area: '57.53',
        yearFounded: '98-102',
        mayor: 'Hubert Bruls',
        website: 'www.nijmegen.nl',
        randomFact: 'the oldest city in the Netherlands, with Roman origins and a rich historical heritage',
        keySectors: 'education, healthcare, and high-tech industries',
        universities: 'Radboud University, HAN University of Applied Sciences',
        sustainability: 'European Green Capital in 2018, with extensive cycling infrastructure and green spaces'
    }
];

// Read the template
const templatePath = path.join(__dirname, 'pages', 'region', 'template.html');
let template = fs.readFileSync(templatePath, 'utf8');

// Create each region page
regions.forEach(region => {
    let pageContent = template;
    
    // Replace placeholders with actual data
    pageContent = pageContent.replace(/REGION_NAME/g, region.name);
    pageContent = pageContent.replace(/DISPLAY_NAME/g, region.displayName);
    pageContent = pageContent.replace(/RANDOM_FACT/g, region.randomFact);
    pageContent = pageContent.replace(/COUNTRY/g, region.country);
    pageContent = pageContent.replace(/POPULATION/g, region.population);
    pageContent = pageContent.replace(/AREA/g, region.area);
    pageContent = pageContent.replace(/YEAR_FOUNDED/g, region.yearFounded);
    pageContent = pageContent.replace(/MAYOR_NAME/g, region.mayor);
    pageContent = pageContent.replace(/REGION_LOWERCASE/g, region.regionLowercase);
    
    // Replace the about section with more specific content
    const aboutSection = `
    <p>${region.displayName} is a beautiful city located in the heart of the KEAN region. Known for ${region.randomFact}, ${region.name} offers a unique blend of traditional charm and modern amenities.</p>
    
    <p>As part of the KEAN initiative, ${region.name} plays a crucial role in fostering cross-border collaboration and cultural exchange between Germany and the Netherlands. The city serves as a hub for ${region.keySectors} in the region.</p>
    
    <h4>Key Features:</h4>
    <ul>
        <li>Population: ${region.population} residents</li>
        <li>Area: ${region.area} square kilometers</li>
        <li>Founded: ${region.yearFounded}</li>
        <li>Mayor: ${region.mayor}</li>
    </ul>
    `;
    
    pageContent = pageContent.replace(/<p>REGION_NAME is a beautiful city located in the heart of the KEAN region. Known for its rich history, vibrant culture, and stunning landscapes, REGION_NAME offers a unique blend of traditional charm and modern amenities.<\/p>\s*<p>As part of the KEAN initiative, REGION_NAME plays a crucial role in fostering cross-border collaboration and cultural exchange between Germany and the Netherlands. The city serves as a hub for innovation, education, and sustainable development in the region.<\/p>/, aboutSection);
    
    // Replace the local economy section
    const economySection = `
    <p>${region.name} boasts a diverse and thriving economy with key sectors including ${region.keySectors}. The city is home to several multinational companies and innovative startups, making it an attractive destination for professionals and entrepreneurs alike.</p>
    
    <h4>Key Economic Sectors:</h4>
    <ul>
        <li>${region.keySectors}</li>
        <li>${region.universities ? 'Education and research institutions' : ''}</li>
        <li>${region.sustainability ? 'Sustainable development initiatives' : ''}</li>
    </ul>
    `;
    
    pageContent = pageContent.replace(/<p>REGION_NAME boasts a diverse and thriving economy with key sectors including technology, manufacturing, tourism, and education. The city is home to several multinational companies and innovative startups, making it an attractive destination for professionals and entrepreneurs alike.<\/p>/, economySection);
    
    // Replace the education section
    const educationSection = `
    <p>${region.universities ? `With its prestigious ${region.universities}, ${region.name} is a center for academic excellence.` : `${region.name} benefits from nearby educational institutions in the KEAN region.`} The city attracts students and researchers from around the world, contributing to its dynamic and international atmosphere.</p>
    
    ${region.universities ? `<h4>Notable Institutions:</h4>
    <ul>
        ${region.universities.split(',').map(uni => `<li>${uni.trim()}</li>`).join('\n        ')}
    </ul>` : ''}
    `;
    
    pageContent = pageContent.replace(/<p>With its prestigious universities and research institutions, REGION_NAME is a center for academic excellence. The city attracts students and researchers from around the world, contributing to its dynamic and international atmosphere.<\/p>/, educationSection);
    
    // Replace the sustainability section
    const sustainabilitySection = `
    <p>${region.name} is committed to sustainability and environmental protection. The city has implemented numerous green initiatives, including ${region.sustainability}.</p>
    
    <h4>Sustainability Highlights:</h4>
    <ul>
        <li>${region.sustainability}</li>
        <li>Renewable energy projects</li>
        <li>Green urban planning</li>
        <li>Waste reduction programs</li>
    </ul>
    `;
    
    pageContent = pageContent.replace(/<p>REGION_NAME is committed to sustainability and environmental protection. The city has implemented numerous green initiatives, including renewable energy projects, sustainable transportation solutions, and urban green spaces.<\/p>/, sustainabilitySection);
    
    // Write the file
    const outputPath = path.join(__dirname, 'pages', 'region', `${region.regionLowercase}.html`);
    fs.writeFileSync(outputPath, pageContent);
    
    console.log(`Generated ${region.name} page at ${outputPath}`);
});

console.log('All region pages have been generated!');
