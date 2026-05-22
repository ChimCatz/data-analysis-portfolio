# Pokemon Data Study: What 1,025 Pokemon Reveal About Type Matchups, Stats, and Rarity

Pokemon has been part of my life since childhood. I first discovered it through **Pokemon Emerald**, and from there I got hooked. I played the mainline Gen 3 games like **Emerald, Sapphire, FireRed, and LeafGreen**, then moved into the Nintendo DS era with **Black, White, Black 2, White 2, HeartGold, and SoulSilver**. Years later, I continued with the Switch titles like **Sword/Shield, Scarlet/Violet, and Legends: Arceus**.

Now that Pokemon continues to stay popular with newer titles like **Pokemon Legends: Z-A**, I wanted to look at the franchise in a different way: not only as a player, but as a data analyst.

For this study, I used a cleaned Pokemon dataset based on public data from Kaggle. The dataset covers **1,025 Pokedex IDs** from **Generation 1 to Generation 9**, with **1,207 total rows** after including alternate forms, Mega Evolutions, Primal forms, Paradox forms, and other special variants.

The final dataset includes the familiar battle stats like **HP, Attack, Defense, Special Attack, Special Defense, and Speed**, but it also includes extra fields such as **type matchups, experience growth, height, weight, base egg steps, base happiness, capture rate, official class, and special group**.

As a long-time Pokemon player, I had several questions in mind:

- Which types are most common?
- Which typings are strongest offensively and defensively?
- Which Pokemon have the highest raw stats in the standard roster?
- Which special-form legendary or mythical entries rise to the top in their own bucket?
- Are defensive Pokemon really slower?
- Are Legendary and Mythical Pokemon actually harder to catch?

This study answers those questions using **Python, pandas, numpy, and matplotlib** inside VS Code.

---

## Section 1: Type Matchups - The Rock-Paper-Scissors System of Pokemon

The first part of the study focuses on Pokemon types.

At first glance, Pokemon type matchups look like a simple rock-paper-scissors system. Fire beats Grass, Water beats Fire, Electric beats Water, and so on. But Pokemon becomes more interesting because many Pokemon have **two types**. A dual-type Pokemon can gain more resistances, more weaknesses, or sometimes both.

To study this, I generated an **18x18 type matchup matrix** and populated it with defensive damage multipliers.

**Chart reference:** `type_matchup_matrix.png`

### Q1: From Generation 1 to 9, which single typing is the most and least common?

The most common single type is **Water**, with **81 single-type Water Pokemon**.

The least common single type is **Flying**, with only **4 single-type Flying Pokemon**.

This makes sense from a game design point of view. Water Pokemon appear across oceans, rivers, lakes, fishing encounters, surfing routes, and many regional Pokedex areas. Flying, on the other hand, is often paired with Normal, so pure Flying Pokemon remain rare.

### Q2: From Generation 1 to 9, which double typing is the most and least common?

The most common dual typing is **Normal/Flying**, with **31 Pokemon**.

Several dual-type combinations appear only once in the dataset. Examples include:

- Fairy/Ice
- Electric/Psychic
- Dragon/Fairy
- Bug/Ghost
- Steel/Water
- Normal/Water
- Ghost/Ice
- Electric/Fire
- Fire/Steel

Normal/Flying being the most common is not surprising. Early-route birds have been a repeated design pattern since Gen 1, and many of them share that typing.

### Q3: Which single typing has the best offensive capability?

**Fighting** and **Ground** are tied as the best offensive single types. Each one hits **5 types** for super-effective damage.

Fighting is strong against:

- Normal
- Ice
- Rock
- Dark
- Steel

Ground is strong against:

- Fire
- Electric
- Poison
- Rock
- Steel

Both are strong offensive types, but they win in different matchups. Fighting is excellent against bulky Normal, Rock, Dark, and Steel Pokemon. Ground is one of the best answers to Electric, Fire, Poison, Rock, and Steel.

### Q4: Which single typing has the best defensive capability?

**Steel** is the best defensive single type, with a defensive score of **10**.

It has **11 resistances** and only **3 weaknesses**, making it one of the strongest defensive types in the game.

This explains why Steel Pokemon often feel hard to break. Even when their stats are not always the highest, their type profile gives them many safe matchups.

### Q5: Which single typing has the worst offensive capability?

**Normal** is the worst offensive single type.

Normal has **0 super-effective matchups**. It does not hit any type for extra damage, and it cannot affect Ghost-type Pokemon at all.

This does not mean Normal Pokemon are useless. Many Normal Pokemon have strong stats or good move pools. But as an attacking type alone, Normal has the weakest offensive coverage.

### Q6: Which single typing has the worst defensive capability?

**Ice** is the worst defensive single type, with a defensive score of **-3**.

Ice has only **1 resistance** and **4 weaknesses**:

- Fire
- Fighting
- Rock
- Steel

This confirms something many players already feel in battle: Ice is dangerous offensively, but fragile defensively.

### Q7: Which double typing has the best offensive capability?

Several dual-type combinations are tied for the best offensive coverage, each with **7 super-effective matchups**.

Examples include:

- Grass/Dark
- Grass/Ice
- Grass/Psychic
- Rock/Fighting
- Rock/Psychic

This shows that dual typing can greatly expand offensive reach. Some combinations cover many more matchups than either type could handle alone.

### Q8: Which double typing has the worst offensive capability?

Several dual-type combinations have only **1 super-effective matchup**.

Examples include:

- Bug/Steel
- Dark/Ghost
- Dark/Poison
- Electric/Water
- Normal/Ghost
- Water/Ground

This is interesting because some of these typings are still good defensively. A typing can be poor offensively but strong as a defensive profile.

### Q9: Which double typing has the best defensive capability?

**Fairy/Steel** and **Steel/Ghost** are tied as the strongest defensive combinations, each with a defensive score of **11**.

These combinations resist many attacker types and have very few bad matchups. This is why Pokemon with these typings often feel difficult to remove from battle.

### Q10: Which double typing has the worst defensive capability?

**Grass/Dragon** and **Ice/Psychic** are tied for the weakest defensive score at **-4**.

Both combinations suffer from several weaknesses and limited resistance value. This makes them harder to use defensively, especially against teams with wide type coverage.

---

## Section 2: Base Stats - Who Looks Strongest on Paper?

After type matchups, the next part of the study focuses on base stats.

Every Pokemon has six main stats:

- HP
- Attack
- Defense
- Special Attack
- Special Defense
- Speed

These numbers shape how a Pokemon performs in battle. A high Attack stat can turn a Pokemon into a physical threat. A high Defense stat can make it hard to knock out. A high Speed stat can decide who moves first.

For the ranking questions in this section, I split the dataset into **two buckets** using the cleaned `standard` flag:

- **Standard pool:** `standard == 1`
- **Special pool:** `standard == 0`

This split solves an important analysis problem. If I rank everything together, special forms and rare high-tier entries immediately dominate the charts. By separating them, I can compare the standard roster on its own and then give legendary, mythical, Mega, Ultra Beast, Paradox, pseudo-legendary, and other non-standard entries their own dedicated leaderboard.

The standard pool contains **990 rows**, while the special pool contains **217 rows** in the current cleaned dataset. This makes the second bucket much more useful than the earlier draft version, because it now captures the full non-standard side of the dataset instead of only a tiny subset.

### Q11A: Which standard-pool Pokemon have the highest total base stats?

In the standard pool, **Slaking** ranks first with **670 total base stats**.

The next few names are **Palafin Hero Form (650)**, **Greninja Ash-Greninja (640)**, and **Wishiwashi School Form (620)**. This is a much more interesting result than the old mixed ranking because it highlights powerful non-legendary roster entries without letting Mega or legendary forms immediately take over the chart.

**Related files:**

- `top10_standard_pool_total.csv`
- `top10_standard_pool_total.png`

### Q11B: Which special-pool Pokemon have the highest total base stats?

In the special pool, **Eternatus Eternamax** ranks first by a huge margin with **1,125 total base stats**.

Behind it are **Mega Mewtwo X**, **Mega Mewtwo Y**, and **Mega Rayquaza**, all tied at **780**, followed by **Primal Groudon** and **Primal Kyogre** at **770**. Once the full non-standard bucket is included, the chart becomes a true ranking of extreme forms rather than a tiny Mega-only snapshot.

**Related files:**

- `top10_special_pool_total.csv`
- `top10_special_pool_total.png`

### Q12A: Which standard-pool Pokemon have the highest Attack?

In the standard pool, **Rampardos** has the highest Attack at **165**.

The next tier includes **Galarian Zen Mode**, **Palafin Hero Form**, and **Slaking**, all at **160**. That is a good reminder that extreme physical power is not limited to legendary or mythical Pokemon. Some standard-pool species still hit incredibly hard on paper.

**Related files:**

- `top10_standard_pool_attack.csv`
- `top10_standard_pool_attack.png`

### Q12B: Which special-pool Pokemon have the highest Attack?

In the special pool, **Mega Mewtwo X** leads with **190 Attack**.

After that come **Mega Heracross (185)**, **Kartana (181)**, **Deoxys Attack Forme (180)**, **Mega Rayquaza (180)**, and **Primal Groudon (180)**. This version of the chart is much richer because it includes Mega forms, Ultra Beasts, Mythicals, and legendary battle forms together.

**Related files:**

- `top10_special_pool_attack.csv`
- `top10_special_pool_attack.png`

### Q13A: Which standard-pool Pokemon have the highest Defense?

In the standard pool, **Shuckle** ranks first with a huge **230 Defense**.

It is followed by other famous walls such as **Steelix (200)**, **Avalugg (184)**, **Hisuian Avalugg (184)**, and **Aggron (180)**. The standard pool makes the defensive specialists stand out much more clearly than the old mixed ranking did.

**Related files:**

- `top10_standard_pool_defense.csv`
- `top10_standard_pool_defense.png`

### Q13B: Which special-pool Pokemon have the highest Defense?

In the special pool, **Eternatus Eternamax** dominates Defense with **250**.

It is followed by **Mega Aggron (230)**, **Mega Steelix (230)**, and **Stakataka (211)**. Compared with the standard pool, the special bucket includes more extreme outliers designed around very high stat ceilings.

**Related files:**

- `top10_special_pool_defense.csv`
- `top10_special_pool_defense.png`

### Q14A: Which standard-pool Pokemon have the highest Special Attack?

In the standard pool, **Greninja Ash-Greninja** ranks first with **153 Special Attack**.

It is followed by **Chandelure**, **Cursola**, and **Vikavolt**, each at **145**. This ranking is more useful than the old version because it highlights elite special attackers that still belong to the regular battle roster.

**Related files:**

- `top10_standard_pool_sp_attack.csv`
- `top10_standard_pool_sp_attack.png`

### Q14B: Which special-pool Pokemon have the highest Special Attack?

In the special pool, **Mega Mewtwo Y** ranks first with **194 Special Attack**.

The next strongest entries are **Deoxys Attack Forme (180)**, **Mega Rayquaza (180)**, **Primal Kyogre (180)**, **Mega Alakazam (175)**, and **Xurkitree (173)**. This is a more convincing special-pool chart because it now reflects several different kinds of non-standard power spikes.

**Related files:**

- `top10_special_pool_sp_attack.csv`
- `top10_special_pool_sp_attack.png`

### Q15A: Which standard-pool Pokemon have the highest Special Defense?

In the standard pool, **Shuckle** also leads Special Defense with **230**.

Behind it are **Florges (154)**, **Carbink (150)**, **Probopass (150)**, and **Toxapex (142)**. This list mixes pure walls with bulky support-oriented species, which gives a better picture of natural special bulk in the main roster.

**Related files:**

- `top10_standard_pool_sp_defense.csv`
- `top10_standard_pool_sp_defense.png`

### Q15B: Which special-pool Pokemon have the highest Special Defense?

In the special pool, **Eternatus Eternamax** ranks first again with **250 Special Defense**.

After that come **Regice (200)**, **Deoxys Defense Forme (160)**, **Primal Kyogre (160)**, **Ho-oh (154)**, and **Lugia (154)**. The special pool is no longer just about offense. It also contains some of the most exaggerated defensive stat profiles in the full dataset.

**Related files:**

- `top10_special_pool_sp_defense.csv`
- `top10_special_pool_sp_defense.png`

### Q16A: Which standard-pool Pokemon are the fastest?

In the standard pool, **Ninjask** is the fastest with a Speed stat of **160**.

It is followed by **Electrode** and **Hisuian Electrode** at **150**, then **Accelgor (145)**. This is a clean example of how speed monsters still exist outside the legendary and special-form tier.

**Related files:**

- `top10_standard_pool_speed.csv`
- `top10_standard_pool_speed.png`

### Q16B: Which special-pool Pokemon are the fastest?

In the special pool, **Regieleki** is the fastest by far with **200 Speed**.

It is followed by **Deoxys Speed Forme (180)**, **Pheromosa (151)**, **Calyrex Shadow Rider (150)**, and several Deoxys and Mega entries close behind. This chart now does a much better job of showing how many speed extremes live in the non-standard pool.

**Related files:**

- `top10_special_pool_speed.csv`
- `top10_special_pool_speed.png`

### Q17: Are Pokemon with higher Defense usually slower?

For the correlation questions, I kept the **full 1,207-row dataset**. The goal here is to test broad stat relationships across the whole project, not only the two leaderboard buckets.

The data does **not** support the idea that Pokemon with higher Defense are usually slower.

The Pearson correlation between Defense and Speed is **-0.0271**, while the Spearman correlation is **0.0300**. Both values are extremely close to zero.

This means there is no clear relationship between Defense and Speed in this dataset. Some defensive Pokemon are slow, but high Defense alone does not strongly predict low Speed.

**Related files:**

- `defense_vs_speed_correlation.png`
- `base_stat_correlation_summary.csv`

### Q18: Are Pokemon with higher Attack usually slower?

The data also does **not** support the idea that high-Attack Pokemon are usually slower.

The Pearson correlation is **0.3337**, and the Spearman correlation is **0.3283**. This is a weak positive relationship, not a negative one.

So in this dataset, higher Attack tends to come with slightly higher Speed on average. The relationship is not strong, but it goes against the idea that physical attackers are usually slow.

**Related files:**

- `attack_vs_speed_correlation.png`
- `base_stat_correlation_summary.csv`

### Q19: Are Pokemon with higher Special Attack usually slower?

The same pattern appears with Special Attack.

The Pearson correlation is **0.3786**, and the Spearman correlation is **0.3631**. This is also a weak positive relationship.

In other words, Pokemon with stronger Special Attack tend to be slightly faster on average, not slower. Again, the relationship is weak, but the trend does not support the idea that stronger special attackers are usually slow.

**Related files:**

- `sp_attack_vs_speed_correlation.png`
- `base_stat_correlation_summary.csv`

---

## Section 3: Capture Rate, Experience Growth, and Official Class

Not every Pokemon is designed to feel the same.

Some Pokemon are common encounters. Some are rare. Some are meant to be late-game challenges. Legendary and Mythical Pokemon often feel harder to catch and slower to train, but I wanted to test whether the dataset supports that idea.

For this section, I compared three fields:

- `capture_rate`
- `experience_growth`
- `official_class`

The official class field groups Pokemon into labels such as **normal, legendary, and mythical**.

### Q20: Do Legendary and Mythical Pokemon generally have lower capture rates?

Yes. Legendary and Mythical Pokemon generally have much lower capture rates.

The mean capture rate is:

- Normal Pokemon: **99.67**
- Legendary Pokemon: **16.65**
- Mythical Pokemon: **9.50**

This shows a clear pattern. Official class is strongly connected to capture difficulty. Legendary and Mythical Pokemon are much harder to catch on average than normal Pokemon.

**Related files:**

- `capture_rate_by_official_class.csv`
- `capture_rate_boxplot_by_class.png`
- `avg_capture_rate_by_class.png`

### Q21: Do Legendary and Mythical Pokemon generally require more experience to reach Level 100?

Yes. Legendary and Mythical Pokemon generally require more experience to reach Level 100.

The mean experience growth is:

- Normal Pokemon: **1,046,900.35**
- Legendary Pokemon: **1,250,000.00**
- Mythical Pokemon: **1,224,648.00**

Legendary Pokemon usually follow the slowest growth curve, while Mythical Pokemon are also much closer to that higher requirement than normal Pokemon.

**Related files:**

- `experience_growth_by_official_class.csv`
- `exp_growth_boxplot_by_class.png`
- `avg_exp_growth_by_class.png`

### Q22: Is capture rate strongly related to experience growth?

Capture rate and experience growth are related, but not strongly enough to explain the full pattern by themselves.

The Pearson correlation is **-0.2512**, and the Spearman correlation is **-0.4004**. This means the relationship is weak to moderate and negative.

Pokemon that need more experience growth tend to have lower capture rates, but the connection is not strong enough on its own. Something else explains the pattern better.

**Related file:**

- `capture_vs_exp_by_class.png`

### Q23: Is official class a stronger signal than raw correlation?

Yes. Official class is a stronger signal than the raw numeric correlation between capture rate and experience growth.

Normal Pokemon have much higher capture rates on average. Legendary and Mythical Pokemon have much lower capture rates and higher experience requirements.

This suggests that the category of the Pokemon explains the pattern better than the numeric relationship alone. In simple terms, being Legendary or Mythical matters more than the raw link between capture rate and experience growth.

**Related files:**

- `official_class_distribution.csv`
- `capture_rate_by_official_class.csv`
- `experience_growth_by_official_class.csv`
- `capture_vs_exp_by_class.png`

---

## Final Thoughts

This Pokemon dataset started as a fun project, but it quickly became a strong data study.

The type matchup section confirmed several long-time player instincts. Water is extremely common. Steel is one of the best defensive types. Ice is dangerous offensively but weak defensively. Dual typing can either create powerful coverage or expose major weaknesses.

The stat section became much clearer after splitting the rankings into two pools. The **standard pool** shows which regular-roster Pokemon stand out on their own terms, while the **special pool** isolates rare high-tier forms instead of letting them distort every chart. That split makes the results easier to interpret and much fairer to compare.

The capture and experience section showed a cleaner pattern. Legendary and Mythical Pokemon are harder to catch and usually require more experience to reach Level 100. The category of the Pokemon explains this better than raw correlation alone.

As a player, these results make the games feel even more intentional. As an analyst, it shows how much structure exists behind a game that many of us first loved as kids.

Pokemon may look simple on the surface, but the numbers behind it tell a deeper story: every type, stat, class, and form is part of a larger design system.

---

## Afterword and Source Credits

This project was made possible through public Pokemon datasets and community-maintained references. I used these sources as the foundation for building, cleaning, validating, and expanding the analysis dataset:

- [Pokemon Dataset by Rounak Banik on Kaggle](https://www.kaggle.com/datasets/rounakbanik/pokemon)
- [All Pokemon Dataset by maca11 on Kaggle](https://www.kaggle.com/datasets/maca11/all-pokemon-dataset)
- [Pokemon Type Chart Gist by armgilles](https://gist.github.com/armgilles/194bcff35001e7eb53a2a8b441e8b2c6)
- [Pokemon Database](https://pokemondb.net/)

The full project files, cleaned dataset work, generated charts, and analysis scripts can be found in my GitHub portfolio repository:

[View the Pokemon Analysis Project on GitHub](https://github.com/ChimCatz/data-analysis-portfolio/tree/main/pokemon_analysis)
