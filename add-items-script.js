(async () => {
  const itemsToAdd = [
    { code: "keep-meals-at-consistent-times", label: "Keep meals at consistent times" },
    { code: "attend-a-group-therapy-session", label: "Attend a group therapy session" },
    { code: "plan-one-activity-that-does-not-involve-substance-use", label: "Plan one activity that does not involve substance use" },
    { code: "take-five-slow-breaths-counting-each-one", label: "Take five slow breaths, counting each one" },
    { code: "practice-one-grounding-technique-in-your-learning-library", label: "Practice one grounding technique in your learning library" },
    { code: "sit-with-both-feet-flat-on-the-floor-and-notice-the-contact", label: "Sit with both feet flat on the floor and notice the contact" },
    { code: "hum-or-sing-along-to-one-song", label: "Hum or sing along to one song" },
    { code: "hold-a-warm-cup-of-tea-or-water-and-notice-the-warmth", label: "Hold a warm cup of tea or water and notice the warmth" },
    { code: "gently-stretch-your-neck-and-shoulders", label: "Gently stretch your neck and shoulders" },
    { code: "dim-the-lights-an-hour-before-bed", label: "Dim the lights an hour before bed" },
    { code: "write-down-tomorrows-worries-before-lying-down", label: "Write down tomorrow's worries before lying down" },
    { code: "one-thing-i-want-to-remember", label: "One thing I want to remember" },
    { code: "care-for-a-plant", label: "Care for a plant" }
  ];

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  console.log(`Starting to add ${itemsToAdd.length} items...`);

  let addedCount = 0;

  for (const item of itemsToAdd) {
    console.log(`Adding: ${item.label} (${item.code})`);

    // Find and click the Add button (usually a button with "Add" text or a plus icon)
    const addBtn = Array.from(document.querySelectorAll('button')).find(el => {
      const t = el.textContent.toLowerCase();
      return t.includes('add') || t.includes('new') || t.includes('create') || t.includes('+');
    });

    if (!addBtn) {
      console.error("Could not find Add button. Please make sure you're on the Support Types page.");
      break;
    }

    addBtn.click();
    await sleep(500);

    // Fill in the form fields
    const inputs = document.querySelectorAll('input');
    let codeInput, labelInput;

    for (const input of inputs) {
      const id = input.id.toLowerCase();
      const name = input.name.toLowerCase();
      const placeholder = input.placeholder.toLowerCase();

      if (id.includes('code') || name.includes('code') || placeholder.includes('code')) {
        codeInput = input;
      }
      if (id.includes('label') || name.includes('label') || placeholder.includes('label') || placeholder.includes('name')) {
        labelInput = input;
      }
    }

    if (codeInput) {
      codeInput.value = item.code;
      codeInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (labelInput) {
      labelInput.value = item.label;
      labelInput.dispatchEvent(new Event('input', { bubbles: true }));
    }

    await sleep(300);

    // Click Save/Submit button
    const saveBtn = Array.from(document.querySelectorAll('button')).find(el => {
      const t = el.textContent.toLowerCase();
      return t.includes('save') || t.includes('submit') || t.includes('ok') || t.includes('confirm');
    });

    if (saveBtn) {
      saveBtn.click();
      console.log(`✓ Added: ${item.label}`);
      addedCount++;
      await sleep(800);
    } else {
      console.error(`Could not find Save button for ${item.label}`);
      break;
    }
  }

  console.log(`Finished! Successfully added ${addedCount} out of ${itemsToAdd.length} items.`);
})();
