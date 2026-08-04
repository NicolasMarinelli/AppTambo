import { useEffect, useRef, useState } from "react";

import { apiClient } from "../api/client";
import type { Animal } from "../api/types";

interface MadreAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
}

export function MadreAutocomplete({ value, onChange }: MadreAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<Animal[]>([]);
  const [showList, setShowList] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (!value) {
      setSuggestions([]);
      return;
    }
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      const { data } = await apiClient.get<Animal[]>("/animals", { params: { search: value } });
      setSuggestions(data);
    }, 250);
    return () => clearTimeout(debounceRef.current);
  }, [value]);

  return (
    <div className="autocomplete">
      <label>
        Madre (caravana)
        <input
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setShowList(true);
          }}
          onFocus={() => setShowList(true)}
          onBlur={() => setTimeout(() => setShowList(false), 150)}
          placeholder="Buscar caravana de la madre..."
        />
      </label>
      {showList && suggestions.length > 0 && (
        <ul className="autocomplete-list">
          {suggestions.map((animal) => (
            <li
              key={animal.id}
              onMouseDown={() => {
                onChange(animal.caravana);
                setShowList(false);
              }}
            >
              {animal.caravana} ({animal.sexo})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
