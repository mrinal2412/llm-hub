import {
    Spinner
  } from "@/components/ui/spinner"

import { Input } from "@/components/ui/input"
import { Resource } from "../projects/ProjectGrid";

export const Combo = (
    {inputValue,
         handleChange,
    loading, items, handleDocSelection}:
     {inputValue: string;
    handleChange: (value:  React.ChangeEvent<HTMLInputElement>) => void;
    loading: boolean;
    items: Resource[];
    handleDocSelection: (value: Resource) => void;
}
) => {
    
    return (

        <div className="col-span-3 bg-white shadow-lg rounded-md relative">
                    <Input

                      value={inputValue}
                      onInput={handleChange}
                      // className="w-full px-4 py-2 border border-gray-300 rounded-md"
                      placeholder="Add any reference document related to projects"
                    />
                    {loading && (
                      <div className="flex items-center justify-center">
                        <Spinner></Spinner>
                      </div>
                    )}
                    {items.length > 0 && (
                      <div className="absolute w-full mt-1 bg-white shadow-lg rounded-md z-10">
                        <div className="text-gray-700">
                          {items.map((item, index) => (
                            <div key={index} className="px-4 py-2 cursor-pointer hover:bg-gray-100" onClick={() => handleDocSelection(item)}>
                              {item.name}
                            </div>
                          ))}
                          {items.length === 0 && !loading && (
                            <div className="px-4 py-2 text-gray-500">No results found.</div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

    )

}