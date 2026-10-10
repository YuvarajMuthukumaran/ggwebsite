(async () => {
  // List of labels that were added by mistake
  const addedLabels = new Set([
    "Thought Record Worksheet", "Making a Safety Plan", "Activity schedule tracker",
    "Behaviour chain analysis", "SMART goals", "Cognitive restructuring technique",
    "Behavioural Experiment planner", "Cognitive disortation checklist", "Core belief worksheet",
    "DBT skills", "Exposure tracking", "Relapse prevention", "Socratic questioning",
    "Problem solving worksheet", "Coping Skills toolbox", "DBT Wise mind worksheet",
    "Sit by a window or outdoors for five minutes", "Drink a glass of water", "Brush teeth",
    "Wash face", "Eat one simple, nourishing snack", "Listen to one favourite song",
    "Open the curtains", "Cook or help prepare one meal", "Spend ten minutes on study or work",
    "Choose one task using a two-minute timer", "Complete one form or phone call", "Bathing",
    "Trimming nails", "Shampooing hair", "Combing hair", "Watch a familiar comedy clip",
    "Have tea or coffee without multitasking", "Draw, colour or work with clay",
    "Sit in a garden or notice three things in nature", "Take a warm shower",
    "Read two pages of a book", "Use music, fragrance or a comforting texture",
    "Look through positive photographs", "Send someone a simple 'hello'",
    "Share a meal with someone", "Call a trusted family member",
    "Sit in a common area for ten minutes", "Attend a support or therapy group",
    "Ask someone to accompany them on a short walk", "Offer a small act of help",
    "Participate in a low-pressure game or activity", "Stretch for three minutes",
    "Walk along the corridor", "Complete one gentle mobility exercise", "Water plants",
    "Walk to a nearby shop with support", "Join supervised yoga or exercise",
    "Spend ten minutes doing light household work", "Read one resource assigned by your care team",
    "Revisit a hobby connected to the patient's identity", "Pray, meditate or engage in a spiritual practice",
    "Care for a plant", "Keep meals at consistent times", "Attend a group therapy session",
    "Plan one activity that does not involve substance use", "Take five slow breaths, counting each one",
    "Practice one grounding technique in your learning library",
    "Sit with both feet flat on the floor and notice the contact", "Hum or sing along to one song",
    "Hold a warm cup of tea or water and notice the warmth", "Gently stretch your neck and shoulders",
    "Dim the lights an hour before bed", "Write down tomorrow's worries before lying down",
    "Keep a consistent wake-up time, even after a poor night", "Put the phone outside arm's reach at bedtime",
    "Play a calming playlist or white noise", "Do a slow body scan lying down",
    "One thing I'm proud of today", "Something that felt heavy today",
    "One thing I want to let go of", "A small win, however minor",
    "Something I'm looking forward to", "One person I'm grateful for and why",
    "Something I handled well under stress", "One thing I want to remember"
  ]);

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  console.log("Searching for mistakenly added items in Support Types...");
  console.log(`Will delete ONLY these exact ${addedLabels.size} labels if found.`);

  let count = 0;
  let safetyLimit = 1000; // Prevent infinite deletion
  let totalProcessed = 0;

  while (totalProcessed < safetyLimit) {
    const rows = Array.from(document.querySelectorAll('tr'));
    let foundToDelete = false;

    for (const row of rows) {
      const cells = row.querySelectorAll('td');

      // Check all columns to find the label column
      for (let colIndex = 0; colIndex < cells.length; colIndex++) {
        const text = cells[colIndex].textContent.trim();

        // Only delete if exact match AND it's one of our target labels
        if (addedLabels.has(text)) {
          console.log(`Found match in column ${colIndex}: "${text}"`);

          const deleteBtn = row.querySelector('button:last-child');
          if (deleteBtn) {
            console.log(`Attempting to delete: "${text}"`);
            deleteBtn.click();
            await sleep(350);

            // Confirm delete modal if present
            const confirmBtn = Array.from(document.querySelectorAll('button')).find(el => {
              const t = el.textContent.toLowerCase();
              return t.includes('delete') || t.includes('confirm') || t.includes('yes') || t.includes('ok');
            });
            if (confirmBtn) {
              confirmBtn.click();
              console.log(`✓ Deleted: "${text}"`);
            }

            count++;
            foundToDelete = true;
            totalProcessed++;
            await sleep(500);
            break; // refresh row selection loop
          }
        }
      }

      if (foundToDelete) break;
    }

    if (!foundToDelete) {
      console.log(`Finished! Successfully removed ${count} incorrect items. Original Support Types kept safe.`);
      break;
    }
  }

  if (totalProcessed >= safetyLimit) {
    console.warn(`Safety limit reached! Processed ${totalProcessed} items. Stopping to prevent accidental deletion.`);
  }
})();
